"""Async settlement input aggregation."""

from __future__ import annotations

import hashlib
from datetime import UTC, datetime

from pydantic import BaseModel, ConfigDict, Field

from app.content.press_types import get_press_type_by_id
from app.domain import (
    Briefing,
    Company,
    DecisionCard,
    Employee,
    GossipLead,
    MemoryWindow,
    MetaProgress,
    PressInput,
    PressType,
    Promise,
    QuarterPhase,
    ScheduledEvent,
    Stats,
    StatsDelta,
)
from app.repo.protocols import GameSessionRepo, MetaProgressRepo, PressArchiveRepo

__all__ = (
    "NoDecisionSelected",
    "NotInSettlementPhase",
    "SettlementAggregatorError",
    "SettlementContext",
    "SettlementInputAggregator",
    "SessionNotFound",
)


class SettlementAggregatorError(Exception):
    """Base error for settlement aggregation failures."""


class SessionNotFound(SettlementAggregatorError):
    """Raised when a session cannot be loaded."""


class NotInSettlementPhase(SettlementAggregatorError):
    """Raised when aggregation starts outside settlement phase."""


class NoDecisionSelected(SettlementAggregatorError):
    """Raised when the quarter has no selected decision."""


class SettlementContext(BaseModel):
    """Frozen snapshot consumed by the async settlement pipeline."""

    model_config = ConfigDict(frozen=True, strict=True)

    session_id: str
    player_id: str
    quarter_number: int = Field(ge=1, le=4)
    company_brief: dict[str, object]
    stats_before_immediate: Stats
    stats_after_immediate: Stats
    selected_decision: DecisionCard
    immediate_effect_applied: StatsDelta
    gossip_collected: list[GossipLead] = Field(default_factory=list)
    press_input: PressInput | None = None
    press_type: PressType | None = None
    press_must_answer: list[str] = Field(default_factory=list)
    active_promises: list[Promise] = Field(default_factory=list)
    agent_memory_window: MemoryWindow
    scheduled_events_firing_this_quarter: list[ScheduledEvent] = Field(default_factory=list)
    history_summary: list[str] = Field(default_factory=list)
    employees_snapshot: list[Employee] = Field(default_factory=list)
    meta_buff_signature: str
    rng_seed_for_aggregation: int
    aggregated_at: datetime


class SettlementInputAggregator:
    """Builds the settlement prompt input from persisted session state."""

    def __init__(
        self,
        session_repo: GameSessionRepo,
        meta_repo: MetaProgressRepo,
        press_archive_repo: PressArchiveRepo,
    ) -> None:
        self.session_repo = session_repo
        self.meta_repo = meta_repo
        self.press_archive_repo = press_archive_repo

    async def build(self, session_id: str) -> SettlementContext:
        session = await self.session_repo.get(session_id)
        if session is None:
            raise SessionNotFound(f"session not found: {session_id}")

        if session.quarter.phase != QuarterPhase.SETTLEMENT:
            raise NotInSettlementPhase(f"cannot aggregate from {session.quarter.phase}")

        selected_id = session.quarter.selected_decision_id
        if not selected_id:
            raise NoDecisionSelected(f"no decision selected for session {session_id}")

        selected_decision = _find_selected_decision(session.quarter.decision_cards, selected_id)
        if selected_decision is None:
            raise NoDecisionSelected(f"selected decision missing: {selected_id}")

        stats_after_immediate = session.stats.model_copy(deep=True)
        stats_before_immediate = stats_after_immediate.apply_delta(
            _negate_stats_delta(selected_decision.immediate_effect),
        )

        press_input = (
            session.quarter.press_input.model_copy(deep=True)
            if session.quarter.press_input
            else None
        )
        press_type = press_input.press_type if press_input is not None else None
        press_must_answer = _build_press_must_answer(press_input)

        current_quarter = session.quarter.number
        active_promises = _build_active_promises(session.promise_log, current_quarter)

        scheduled_events = [
            event.model_copy(deep=True)
            for event in session.scheduled_events
            if event.fire_quarter == current_quarter and not event.resolved
        ]

        meta = await self.meta_repo.get(session.player_id)

        company_brief = _build_company_brief(session.company, session.quarter.briefing)
        meta_buff_signature = _build_meta_buff_signature(meta)
        aggregated_at = datetime.now(UTC)

        return SettlementContext(
            session_id=session.id,
            player_id=session.player_id,
            quarter_number=current_quarter,
            company_brief=company_brief,
            stats_before_immediate=stats_before_immediate,
            stats_after_immediate=stats_after_immediate,
            selected_decision=selected_decision.model_copy(deep=True),
            immediate_effect_applied=selected_decision.immediate_effect.model_copy(deep=True),
            gossip_collected=[
                lead.model_copy(deep=True) for lead in session.quarter.collected_leads
            ],
            press_input=press_input,
            press_type=press_type,
            press_must_answer=press_must_answer,
            active_promises=active_promises,
            agent_memory_window=session.agent_memory.model_copy(deep=True),
            scheduled_events_firing_this_quarter=scheduled_events,
            history_summary=[entry.settlement_summary for entry in session.history],
            employees_snapshot=[_sanitize_employee(employee) for employee in session.employees],
            meta_buff_signature=meta_buff_signature,
            rng_seed_for_aggregation=_build_rng_seed(
                session.id,
                session.player_id,
                current_quarter,
                selected_id,
                stats_after_immediate,
            ),
            aggregated_at=aggregated_at,
        )


def _find_selected_decision(cards: list[DecisionCard], selected_id: str) -> DecisionCard | None:
    for card in cards:
        if card.id == selected_id:
            return card
    return None


def _negate_stats_delta(delta: StatsDelta) -> StatsDelta:
    return StatsDelta(
        CASH=-delta.CASH if delta.CASH is not None else None,
        MORALE=-delta.MORALE if delta.MORALE is not None else None,
        BOARD=-delta.BOARD if delta.BOARD is not None else None,
        FACE=-delta.FACE if delta.FACE is not None else None,
    )


def _build_press_must_answer(press_input: PressInput | None) -> list[str]:
    if press_input is None:
        return []
    entry = get_press_type_by_id(press_input.press_type.value)
    if entry is None:
        return []
    return list(entry.get("must_answer_topics", []))


def _build_active_promises(promises: list[Promise], current_quarter: int) -> list[Promise]:
    active: list[Promise] = []
    for promise in promises:
        if promise.fulfilled is not None or promise.judged_at_quarter is not None:
            continue
        if promise.quarter_made >= current_quarter:
            continue
        parsed = promise.parsed
        if parsed is None or parsed.deadline_quarter is None:
            continue
        if parsed.deadline_quarter > current_quarter:
            continue
        active.append(promise.model_copy(deep=True))
    return active


def _build_company_brief(
    company: Company,
    briefing: Briefing | None,
) -> dict[str, object]:
    death_causes = getattr(company, "death_causes", [])
    hidden_risks = []
    if briefing is not None:
        hidden_risks = list(getattr(briefing, "hidden_risks", []))

    return {
        "name": company.name,
        "business": company.business,
        "founding_motto": company.founding_motto,
        "deathCausesSummary": [cause.description for cause in death_causes],
        "hiddenRisks": hidden_risks,
    }


def _sanitize_employee(employee: Employee) -> Employee:
    return employee.model_copy(deep=True, update={"hidden_secrets": []})


def _build_meta_buff_signature(meta: MetaProgress) -> str:
    parts = [
        unlock.effect_summary.strip()
        for unlock in meta.unlocked_legacies
        if unlock.effect_summary.strip()
    ]
    return "/".join(parts)


def _build_rng_seed(
    session_id: str,
    player_id: str,
    quarter_number: int,
    selected_decision_id: str,
    stats_after_immediate: Stats,
) -> int:
    payload = (
        f"{session_id}|{player_id}|{quarter_number}|{selected_decision_id}|"
        f"{stats_after_immediate.CASH},{stats_after_immediate.MORALE},"
        f"{stats_after_immediate.BOARD},{stats_after_immediate.FACE}"
    )
    digest = hashlib.sha256(payload.encode("utf-8")).digest()
    return int.from_bytes(digest[:8], "big")
