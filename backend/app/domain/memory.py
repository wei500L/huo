"""Memory domain models."""

from __future__ import annotations

from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from .stats import StatsDelta

__all__ = ("MemoryActor", "MemoryEntry", "MemoryWindow", "ScheduledEvent")


class MemoryActor(StrEnum):
    """Actor categories that hold memories."""

    BOARD = "BOARD"
    EMPLOYEE = "EMPLOYEE"
    MEDIA = "MEDIA"
    RIVAL = "RIVAL"


class MemoryEntry(BaseModel):
    """A frozen memory shard used for recall and prompt assembly."""

    model_config = ConfigDict(frozen=True, strict=True)

    id: str
    actor: MemoryActor
    actor_id: str | None = None
    quarter: int = Field(ge=1, le=4)
    event_type: Literal[
        "decision_seen",
        "promise_made",
        "promise_broken",
        "layoff",
        "press_quote",
        "betrayal",
        "favor",
    ]
    summary: str = Field(max_length=80)
    weight: int = Field(default=3, ge=1, le=5)


class MemoryWindow(BaseModel):
    """A bounded memory slice for async settlement prompt construction."""

    model_config = ConfigDict(strict=True)

    entries: list[MemoryEntry]
    max_size: int = 6

    def append(self, entry: MemoryEntry) -> MemoryWindow:
        """Return a new window sorted by quarter desc, weight desc, then truncated."""

        entries = [*self.entries, entry]
        sorted_entries = sorted(
            entries,
            key=lambda item: (item.quarter, item.weight),
            reverse=True,
        )
        return type(self)(entries=sorted_entries[: self.max_size], max_size=self.max_size)


class ScheduledEvent(BaseModel):
    """A delayed consequence that fires in a later quarter."""

    model_config = ConfigDict(frozen=True, strict=True)

    id: str
    source_decision_id: str
    fire_quarter: int = Field(ge=1, le=4)
    description: str = Field(max_length=60)
    effect_on_fire: StatsDelta
    resolved: bool = False
