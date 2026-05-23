"""Quarter lifecycle state machine."""

from __future__ import annotations

import asyncio
import random

from pydantic import BaseModel, ConfigDict

from app.domain import Briefing, DeathReason, HistoryEntry, Quarter, QuarterPhase, Settlement
from app.repo.protocols import GameSession, GameSessionRepo

from .company_service import _make_briefing

__all__ = (
    "FinishResult",
    "IllegalTransitionError",
    "QuarterStateMachine",
    "StateMachineError",
    "WrongQuarterError",
)

_TRANSITIONS: dict[QuarterPhase, set[QuarterPhase]] = {
    QuarterPhase.BRIEFING: {QuarterPhase.GOSSIP},
    QuarterPhase.GOSSIP: {QuarterPhase.DECISION},
    QuarterPhase.DECISION: {QuarterPhase.PRESS, QuarterPhase.SETTLEMENT},
    QuarterPhase.PRESS: {QuarterPhase.SETTLEMENT},
    QuarterPhase.SETTLEMENT: {QuarterPhase.DONE},
    QuarterPhase.DONE: set(),
}


class StateMachineError(Exception):
    """Base error for quarter state machine failures."""


class IllegalTransitionError(StateMachineError):
    """Raised when a phase transition skips or violates the lifecycle."""


class WrongQuarterError(StateMachineError):
    """Raised when a quarter-scoped payload targets another quarter."""


class FinishResult(BaseModel):
    """Terminal or advancement result for a completed settlement."""

    model_config = ConfigDict(frozen=True, strict=True)

    dead: bool = False
    reason: DeathReason | None = None
    won: bool = False
    next_quarter: int | None = None


class QuarterStateMachine:
    """Owns quarter phase changes and terminal session status decisions."""

    def __init__(self, session_repo: GameSessionRepo) -> None:
        self.session_repo = session_repo
        self._locks: dict[str, asyncio.Lock] = {}
        self._locks_guard = asyncio.Lock()

    async def transition_to(self, session_id: str, target_phase: QuarterPhase) -> GameSession:
        async with await self._session_lock(session_id):
            return await self._transition_to_unlocked(session_id, target_phase)

    async def enter_decision_phase(self, session_id: str) -> GameSession:
        return await self.transition_to(session_id, QuarterPhase.DECISION)

    async def enter_press_phase(self, session_id: str) -> GameSession:
        return await self.transition_to(session_id, QuarterPhase.PRESS)

    async def enter_settlement_phase(self, session_id: str) -> GameSession:
        return await self.transition_to(session_id, QuarterPhase.SETTLEMENT)

    async def finish_settlement(
        self,
        session_id: str,
        settlement: Settlement,
    ) -> tuple[GameSession, FinishResult]:
        async with await self._session_lock(session_id):
            session = await self._load_session(session_id)
            if session.quarter.phase != QuarterPhase.SETTLEMENT:
                raise IllegalTransitionError(
                    f"cannot finish settlement from {session.quarter.phase}",
                )
            if settlement.quarter != session.quarter.number:
                raise WrongQuarterError(
                    f"settlement quarter {settlement.quarter} does not match "
                    f"current quarter {session.quarter.number}",
                )

            stats_before = session.stats
            stats_after = stats_before.apply_delta(settlement.metrics_delta)
            quarter = session.quarter.model_copy(
                update={"settlement": settlement, "phase": QuarterPhase.DONE},
            )
            history = [
                *session.history,
                HistoryEntry(
                    quarter=quarter.number,
                    decision_id=quarter.selected_decision_id or "",
                    press_bundle_id=None,
                    stats_before=stats_before,
                    stats_after=stats_after,
                    settlement_summary=settlement.quarter_report[:60],
                ),
            ]

            death_reason = stats_after.is_dead()
            if death_reason is not None:
                dead_session = session.model_copy(
                    update={
                        "quarter": quarter,
                        "stats": stats_after,
                        "history": history,
                        "status": "dead",
                    },
                )
                saved = await self.session_repo.save(dead_session)
                return saved, FinishResult(dead=True, reason=death_reason)

            if quarter.number == 4:
                won_session = session.model_copy(
                    update={
                        "quarter": quarter,
                        "stats": stats_after,
                        "history": history,
                        "status": "won",
                    },
                )
                saved = await self.session_repo.save(won_session)
                return saved, FinishResult(won=True)

            settled_session = session.model_copy(
                update={"quarter": quarter, "stats": stats_after, "history": history},
            )
            saved = await self.session_repo.save(settled_session)
            advanced = await self._advance_to_next_quarter_unlocked(saved.id)
            return advanced, FinishResult(next_quarter=advanced.quarter.number)

    async def advance_to_next_quarter(self, session_id: str) -> GameSession:
        async with await self._session_lock(session_id):
            return await self._advance_to_next_quarter_unlocked(session_id)

    async def _session_lock(self, session_id: str) -> asyncio.Lock:
        async with self._locks_guard:
            lock = self._locks.get(session_id)
            if lock is None:
                lock = asyncio.Lock()
                self._locks[session_id] = lock
            return lock

    async def _transition_to_unlocked(
        self,
        session_id: str,
        target_phase: QuarterPhase,
    ) -> GameSession:
        session = await self._load_session(session_id)
        self._validate_transition(session, target_phase)
        quarter = session.quarter.model_copy(update={"phase": target_phase})
        return await self.session_repo.save(session.model_copy(update={"quarter": quarter}))

    async def _advance_to_next_quarter_unlocked(self, session_id: str) -> GameSession:
        session = await self._load_session(session_id)
        quarter = session.quarter
        if session.status != "active":
            raise IllegalTransitionError("only active sessions can advance")
        if quarter.phase != QuarterPhase.DONE or quarter.settlement is None:
            raise IllegalTransitionError("settlement must be completed before advancing")
        if quarter.number >= 4:
            raise IllegalTransitionError("quarter 4 cannot advance")

        next_number = quarter.number + 1
        next_quarter = Quarter(
            number=next_number,
            phase=QuarterPhase.BRIEFING,
            briefing=_make_next_briefing(session, next_number),
        )
        return await self.session_repo.save(session.model_copy(update={"quarter": next_quarter}))

    async def _load_session(self, session_id: str) -> GameSession:
        session = await self.session_repo.get(session_id)
        if session is None:
            raise StateMachineError(f"session not found: {session_id}")
        return session

    def _validate_transition(self, session: GameSession, target_phase: QuarterPhase) -> None:
        if session.status != "active":
            raise IllegalTransitionError("only active sessions can transition")

        current_phase = session.quarter.phase
        if target_phase not in _TRANSITIONS[current_phase]:
            raise IllegalTransitionError(
                f"cannot transition from {current_phase} to {target_phase}",
            )

        quarter_number = session.quarter.number
        if current_phase == QuarterPhase.DECISION:
            if target_phase == QuarterPhase.PRESS and quarter_number != 3:
                raise IllegalTransitionError("press phase is only available in quarter 3")
            if target_phase == QuarterPhase.SETTLEMENT and quarter_number == 3:
                raise IllegalTransitionError("quarter 3 must enter press before settlement")


def _make_next_briefing(session: GameSession, quarter_number: int) -> Briefing:
    seed = f"{session.id}:{quarter_number}:{len(session.history)}"
    return _make_briefing(quarter_number, session.company, random.Random(seed))
