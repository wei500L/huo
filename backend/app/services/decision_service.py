"""Decision phase application service."""

from __future__ import annotations

import random
from collections.abc import Callable
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict

from app.content import sample_decision_cards
from app.domain import (
    BoomerangSeed,
    DecisionCard,
    DecisionCategory,
    PromiseSource,
    QuarterPhase,
    ScheduledEvent,
    Stats,
    StatsDelta,
)
from app.repo.protocols import GameSession, GameSessionRepo
from app.services.promise_extractor import extract_promises
from app.services.quarter_state_machine import QuarterStateMachine

__all__ = (
    "CardNotInDraw",
    "DecisionNotFound",
    "DecisionResult",
    "DecisionService",
    "DecisionServiceError",
    "InvalidPhaseForDecision",
)


class DecisionServiceError(Exception):
    """Base error for decision service failures."""


class DecisionNotFound(DecisionServiceError):
    """Raised when a session cannot be loaded for a decision operation."""


class InvalidPhaseForDecision(DecisionServiceError):
    """Raised when a decision operation is attempted in the wrong phase."""


class CardNotInDraw(DecisionServiceError):
    """Raised when the selected card was not part of the current draw."""


class DecisionResult(BaseModel):
    """Result returned after selecting one decision card."""

    model_config = ConfigDict(frozen=True, strict=True)

    session_id: str
    new_stats: Stats
    selected_card_id: str
    new_scheduled_event_ids: list[str]
    new_promise_ids: list[str]
    should_enter_press: bool
    next_phase_hint: Literal["PRESS", "SETTLEMENT"]


class DecisionService:
    """Owns decision-card draws and immediate selection effects."""

    def __init__(
        self,
        session_repo: GameSessionRepo,
        state_machine: QuarterStateMachine,
        rng_factory: Callable[[int | None], random.Random] = random.Random,
    ) -> None:
        self.session_repo = session_repo
        self.state_machine = state_machine
        self.rng_factory = rng_factory

    async def draw_decision_cards(
        self,
        session_id: str,
        rng_seed: int | None = None,
    ) -> GameSession:
        session = await self._load_session(session_id)
        self._validate_draw_allowed(session)

        sampled = sample_decision_cards(
            n=3,
            quarter=session.quarter.number,
            current_stats=session.stats,
            rng_seed=rng_seed,
        )
        decision_cards = [_build_decision_card(card) for card in sampled]
        quarter = session.quarter.model_copy(update={"decision_cards": decision_cards})
        return await self.session_repo.save(session.model_copy(update={"quarter": quarter}))

    async def select_decision(
        self,
        session_id: str,
        card_id: str,
        rng_seed: int | None = None,
    ) -> DecisionResult:
        session = await self._load_session(session_id)
        if session.quarter.phase != QuarterPhase.DECISION:
            raise InvalidPhaseForDecision(
                f"cannot select decision from {session.quarter.phase}",
            )

        card = _find_drawn_card(session.quarter.decision_cards, card_id)
        if card is None:
            raise CardNotInDraw(f"card not in current draw: {card_id}")

        rng = self.rng_factory(rng_seed)
        new_stats = session.stats.apply_delta(card.immediate_effect)
        new_scheduled_events = _schedule_boomerangs(session, card, rng)
        promise_text = f"{card.flavor} {card.description}".strip()
        new_promises = extract_promises(
            promise_text,
            PromiseSource.DECISION_FLAVOR,
            session.quarter.number,
        )

        quarter = session.quarter.model_copy(update={"selected_decision_id": card.id})
        updated = session.model_copy(
            update={
                "stats": new_stats,
                "quarter": quarter,
                "scheduled_events": [*session.scheduled_events, *new_scheduled_events],
                "promise_log": [*session.promise_log, *new_promises],
            },
        )
        await self.session_repo.save(updated)

        should_enter_press = session.quarter.number == 3
        return DecisionResult(
            session_id=session.id,
            new_stats=new_stats,
            selected_card_id=card.id,
            new_scheduled_event_ids=[event.id for event in new_scheduled_events],
            new_promise_ids=[promise.id for promise in new_promises],
            should_enter_press=should_enter_press,
            next_phase_hint="PRESS" if should_enter_press else "SETTLEMENT",
        )

    async def _load_session(self, session_id: str) -> GameSession:
        session = await self.session_repo.get(session_id)
        if session is None:
            raise DecisionNotFound(f"session not found: {session_id}")
        return session

    def _validate_draw_allowed(self, session: GameSession) -> None:
        phase = session.quarter.phase
        if phase == QuarterPhase.GOSSIP:
            return
        if phase == QuarterPhase.DECISION and not session.quarter.decision_cards:
            return
        raise InvalidPhaseForDecision(f"cannot draw decision cards from {phase}")


def _build_decision_card(payload: dict[str, Any]) -> DecisionCard:
    return DecisionCard(
        id=str(payload["id"]),
        category=DecisionCategory(str(payload["category"])),
        title=str(payload["title"]),
        description=str(payload["description"]),
        immediate_effect=StatsDelta(**payload["immediate_effect"]),
        flavor=str(payload["flavor"]),
        long_term_hint=payload.get("long_term_hint"),
        boomerang_seeds=[
            BoomerangSeed(
                delay_quarters=seed["delay_quarters"],
                probability=seed["probability"],
                description=seed["description"],
                effect=StatsDelta(**seed["effect"]),
            )
            for seed in payload.get("boomerang_seeds", [])
        ],
    )


def _find_drawn_card(cards: list[DecisionCard], card_id: str) -> DecisionCard | None:
    for card in cards:
        if card.id == card_id:
            return card
    return None


def _schedule_boomerangs(
    session: GameSession,
    card: DecisionCard,
    rng: random.Random,
) -> list[ScheduledEvent]:
    scheduled: list[ScheduledEvent] = []
    for seed in card.boomerang_seeds:
        if rng.random() >= seed.probability:
            continue
        fire_quarter = session.quarter.number + seed.delay_quarters
        if fire_quarter > 4:
            continue
        scheduled.append(
            ScheduledEvent(
                id=f"SE-{rng.getrandbits(40):010x}",
                source_decision_id=card.id,
                fire_quarter=fire_quarter,
                description=seed.description,
                effect_on_fire=seed.effect,
                resolved=False,
            ),
        )
    return scheduled
