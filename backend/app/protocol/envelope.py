"""Protocol envelope wrapper."""

from __future__ import annotations

import re
from datetime import UTC, datetime
from enum import StrEnum
from typing import Generic, TypeVar
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, field_validator

__all__ = ("AckPayload", "Envelope", "MessageDirection")

T = TypeVar("T", bound=BaseModel)


class MessageDirection(StrEnum):
    INBOUND = "INBOUND"
    OUTBOUND = "OUTBOUND"


class AckPayload(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")

    ok: bool
    reason: str | None = None
    retry_after_ms: int | None = None


class Envelope(BaseModel, Generic[T]):
    model_config = ConfigDict(strict=True, extra="forbid")

    v: int = 1
    id: str = Field(default_factory=lambda: str(uuid4()))
    ts: datetime = Field(default_factory=lambda: datetime.now(UTC))
    direction: MessageDirection
    type: str
    ack_for: str | None = None
    payload: T

    @field_validator("id")
    @classmethod
    def _validate_uuid4(cls, value: str) -> str:
        parsed = UUID(value)
        if parsed.version != 4:
            raise ValueError("id must be a uuid4")
        return str(parsed)

    @classmethod
    def wrap(cls, direction: MessageDirection, msg: T) -> Envelope[T]:
        return cls(
            direction=direction,
            type=_snake_case(msg.__class__.__name__),
            payload=msg,
        )


_SNAKE_CASE_PATTERN = re.compile(r"(?<!^)(?=[A-Z])")


def _snake_case(name: str) -> str:
    return _SNAKE_CASE_PATTERN.sub("_", name).lower()
