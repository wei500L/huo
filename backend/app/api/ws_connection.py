"""Shared websocket connection utilities."""

from __future__ import annotations

import asyncio
import json
import re
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any
from uuid import UUID, uuid4

from fastapi import WebSocket
from pydantic import BaseModel, ConfigDict, Field, field_validator
from pydantic.alias_generators import to_camel

from app.protocol import (
    AckPayload,
    Envelope,
    ErrorOutbound,
    GameSnapshot,
    MessageDirection,
    Toast,
)
from app.repo.protocols import GameSessionRepo, MetaProgressRepo
from app.services import (
    DecisionNotFound,
    GossipServiceError,
    InsufficientAP,
    InvalidPhaseForDecision,
    InvalidPhaseForGossip,
    InvalidPressPhase,
    PressInputServiceError,
    SessionNotFound,
    StateMachineError,
    TranscriptRejected,
    WrongPressQuarter,
)

__all__ = ("InboundEnvelope", "PING_INTERVAL_S", "connection_manager")

PING_INTERVAL_S = 30.0
_PING_MISS_LIMIT = 2
_SNAKE_CASE_PATTERN = re.compile(r"(?<!^)(?=[A-Z])")


@dataclass(slots=True)
class _ConnectionRecord:
    websocket: WebSocket
    session_id: str | None = None


class ConnectionManager:
    """Keep websocket connections keyed by player."""

    def __init__(self) -> None:
        self._connections: dict[str, _ConnectionRecord] = {}
        self._lock = asyncio.Lock()

    async def on_connect(
        self,
        player_id: str,
        websocket: WebSocket,
        session_id: str | None = None,
    ) -> None:
        async with self._lock:
            self._connections[player_id] = _ConnectionRecord(
                websocket=websocket, session_id=session_id
            )

    async def bind_session(self, player_id: str, session_id: str) -> None:
        async with self._lock:
            record = self._connections.get(player_id)
            if record is not None:
                record.session_id = session_id

    async def on_disconnect(self, player_id: str) -> None:
        async with self._lock:
            self._connections.pop(player_id, None)

    async def send_to_player(self, player_id: str, envelope: Envelope[BaseModel]) -> None:
        async with self._lock:
            record = self._connections.get(player_id)
        if record is None:
            return
        try:
            await record.websocket.send_text(_envelope_json(envelope))
        except Exception:
            return

    async def broadcast_to_session(self, session_id: str, envelope: Envelope[BaseModel]) -> None:
        async with self._lock:
            targets = [
                record.websocket
                for record in self._connections.values()
                if record.session_id == session_id
            ]
        for websocket in targets:
            try:
                await websocket.send_text(_envelope_json(envelope))
            except Exception:
                continue


connection_manager = ConnectionManager()


class InboundEnvelope(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid", populate_by_name=True, alias_generator=to_camel)

    v: int = 1
    id: str = Field(default_factory=lambda: str(uuid4()))
    ts: datetime = Field(default_factory=lambda: datetime.now(UTC))
    direction: MessageDirection
    type: str
    ack_for: str | None = None
    payload: dict[str, Any]

    @field_validator("direction", mode="before")
    @classmethod
    def _normalize_direction(cls, value: str) -> str:
        if isinstance(value, str):
            return value.upper()
        return value

    @field_validator("id")
    @classmethod
    def _validate_uuid4(cls, value: str) -> str:
        parsed = UUID(value)
        if parsed.version != 4:
            raise ValueError("id must be a uuid4")
        return str(parsed)


async def _snapshot_for_session(
    session_id: str,
    session_repo: GameSessionRepo,
    meta_repo: MetaProgressRepo,
) -> GameSnapshot:
    session = await session_repo.get(session_id)
    if session is None:
        raise SessionNotFound(f"session not found: {session_id}")
    return GameSnapshot.from_domain(
        session_id=session.id,
        player_id=session.player_id,
        company=session.company,
        stats=session.stats,
        quarter=session.quarter,
        history=session.history,
        meta_progress=await meta_repo.get(session.player_id),
        promise_log=session.promise_log,
        status=session.status,
    )


def _wrap_outbound(
    payload: BaseModel,
    ack_for: str | None = None,
    *,
    type_name: str | None = None,
) -> Envelope[BaseModel]:
    return Envelope[BaseModel](
        direction=MessageDirection.OUTBOUND,
        type=type_name or _snake_case(payload.__class__.__name__),
        ack_for=ack_for,
        payload=payload,
    )


def _envelope_json(envelope: Envelope[BaseModel]) -> str:
    data = envelope.model_dump(mode="json", by_alias=True)
    data["direction"] = data["direction"].lower()
    if isinstance(envelope.payload, BaseModel):
        data["payload"] = envelope.payload.model_dump(mode="json", by_alias=True)
    return json.dumps(data, ensure_ascii=False)


def _snake_case(name: str) -> str:
    return _SNAKE_CASE_PATTERN.sub("_", name).lower()


def _error_envelope(
    code: str,
    message: str,
    retryable: bool,
    ack_for: str | None = None,
    flags: list[str] | None = None,
) -> Envelope[BaseModel]:
    return _wrap_outbound(
        ErrorOutbound(code=code, message=message, retryable=retryable, flags=flags or []),
        ack_for=ack_for,
        type_name="error",
    )


def _ack_envelope(ack_for: str | None = None, reason: str | None = None) -> Envelope[BaseModel]:
    return _wrap_outbound(AckPayload(ok=True, reason=reason), ack_for, type_name="ack")


def _ping_envelope() -> Envelope[BaseModel]:
    return _wrap_outbound(Toast(level="info", message="ping"), type_name="toast")


def _toast(message: str, ack_for: str | None = None) -> Envelope[BaseModel]:
    return _wrap_outbound(Toast(level="info", message=message), ack_for=ack_for)


async def _send(player_id: str, envelope: Envelope[BaseModel]) -> None:
    await connection_manager.send_to_player(player_id, envelope)


async def _send_snapshot(
    player_id: str,
    session_id: str,
    session_repo: GameSessionRepo,
    meta_repo: MetaProgressRepo,
    ack_for: str | None = None,
) -> None:
    snapshot = await _snapshot_for_session(session_id, session_repo, meta_repo)
    await _send(player_id, _wrap_outbound(snapshot, ack_for))


def _inbound_message(raw_text: str) -> InboundEnvelope:
    return InboundEnvelope.model_validate_json(raw_text)


def _invalid_message_error(ack_for: str | None = None) -> Envelope[BaseModel]:
    return _error_envelope("invalid_message", "unsupported message type", False, ack_for)


def _map_exception(exc: Exception, ack_for: str | None = None) -> Envelope[BaseModel]:
    if isinstance(exc, SessionNotFound):
        return _error_envelope("session_not_found", "session not found", False, ack_for)
    if isinstance(exc, DecisionNotFound):
        return _error_envelope("session_not_found", "session not found", False, ack_for)
    if isinstance(exc, GossipServiceError) and "session not found" in str(exc).lower():
        return _error_envelope("session_not_found", "session not found", False, ack_for)
    if isinstance(exc, PressInputServiceError) and "session not found" in str(exc).lower():
        return _error_envelope("session_not_found", "session not found", False, ack_for)
    if isinstance(exc, TranscriptRejected):
        return _error_envelope(
            "transcript_rejected", "transcript rejected", False, ack_for, exc.flags
        )
    if isinstance(exc, InvalidPhaseForDecision):
        return _error_envelope("invalid_phase", str(exc), False, ack_for)
    if isinstance(exc, InvalidPhaseForGossip):
        return _error_envelope("invalid_phase", str(exc), False, ack_for)
    if isinstance(exc, InvalidPressPhase):
        return _error_envelope("invalid_phase", str(exc), False, ack_for)
    if isinstance(exc, WrongPressQuarter):
        return _error_envelope("wrong_quarter", str(exc), False, ack_for)
    if isinstance(exc, InsufficientAP):
        return _error_envelope("insufficient_ap", str(exc), False, ack_for)
    if isinstance(exc, StateMachineError):
        code = (
            "session_not_found"
            if "session not found" in str(exc).lower()
            else "state_machine_error"
        )
        message = "session not found" if code == "session_not_found" else "illegal state transition"
        return _error_envelope(code, message, False, ack_for)
    return _error_envelope("internal_error", "internal server error", False, ack_for)
