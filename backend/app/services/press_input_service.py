"""Realtime press transcript intake service."""

from __future__ import annotations

from datetime import UTC, datetime

from pydantic import BaseModel, ConfigDict, Field

from app.content.press_types import get_press_type_by_id
from app.domain import PressInput, PressType, QuarterPhase
from app.repo.protocols import GameSession, GameSessionRepo
from app.safety import clean_transcript
from app.services.quarter_state_machine import QuarterStateMachine

__all__ = (
    "InvalidPressPhase",
    "PressInputService",
    "PressInputServiceError",
    "SubmitPressResult",
    "TranscriptRejected",
    "WrongPressQuarter",
)


class PressInputServiceError(Exception):
    """Base error for press transcript intake."""


class WrongPressQuarter(PressInputServiceError):
    """Raised when the transcript is submitted outside quarter three."""


class TranscriptRejected(PressInputServiceError):
    """Raised when the cleaned transcript is not accepted."""

    def __init__(
        self,
        message: str,
        *,
        flags: list[str] | None = None,
        hits: list[str] | None = None,
    ) -> None:
        super().__init__(message)
        self.flags = list(flags or [])
        self.hits = list(hits or [])


class InvalidPressPhase(PressInputServiceError):
    """Raised when the press phase is not ready for transcript intake."""


class SubmitPressResult(BaseModel):
    """Service response for a stored transcript."""

    model_config = ConfigDict(frozen=True, strict=True)

    accepted: bool
    flags: list[str] = Field(default_factory=list)
    replaced_count: int = 0
    press_input_quarter: int


class PressInputService:
    """Store cleaned press transcripts on the session."""

    def __init__(
        self,
        session_repo: GameSessionRepo,
        state_machine: QuarterStateMachine | None = None,
    ) -> None:
        self.session_repo = session_repo
        self.state_machine = state_machine

    async def submit(
        self,
        session_id: str,
        press_type: PressType,
        transcript: str,
        duration_s: float | None = None,
    ) -> SubmitPressResult:
        session = await self._load_session(session_id)
        self._validate_session(session)

        result = clean_transcript(transcript)
        if result.rejected:
            raise TranscriptRejected(
                "transcript rejected",
                flags=result.flags,
                hits=result.hits,
            )

        press_type_entry = get_press_type_by_id(press_type.value)
        if press_type_entry is None:
            raise PressInputServiceError(f"unknown press type: {press_type.value}")

        press_input = PressInput(
            quarter=session.quarter.number,
            press_type=press_type,
            must_answer_topics=list(press_type_entry["must_answer_topics"]),
            transcript=result.cleaned,
            duration_s=duration_s,
            word_count=len(result.cleaned),
            flags=list(result.flags),
            submitted_at=datetime.now(UTC),
        )
        updated_quarter = session.quarter.model_copy(update={"press_input": press_input})
        updated_session = session.model_copy(update={"quarter": updated_quarter})
        await self.session_repo.save(updated_session)
        if self.state_machine is not None:
            await self.state_machine.enter_settlement_phase(session_id)

        return SubmitPressResult(
            accepted=True,
            flags=list(result.flags),
            replaced_count=result.replaced_count,
            press_input_quarter=press_input.quarter,
        )

    async def _load_session(self, session_id: str) -> GameSession:
        session = await self.session_repo.get(session_id)
        if session is None:
            raise PressInputServiceError(f"session not found: {session_id}")
        return session

    def _validate_session(self, session: GameSession) -> None:
        if session.quarter.number != 3:
            raise WrongPressQuarter(
                f"press input only allowed in quarter 3: {session.quarter.number}",
            )
        if session.quarter.phase != QuarterPhase.PRESS:
            raise InvalidPressPhase(
                f"press input only allowed in PRESS phase: {session.quarter.phase}",
            )
