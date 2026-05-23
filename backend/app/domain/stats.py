"""Company health stats domain model."""

from __future__ import annotations

from enum import StrEnum
from random import Random

from pydantic import BaseModel, ConfigDict, Field

__all__ = ("DeathReason", "Stats", "StatsDelta")


class DeathReason(StrEnum):
    """Terminal company failure categories."""

    BANKRUPTCY = "BANKRUPTCY"
    MORALE_COLLAPSE = "MORALE_COLLAPSE"
    OUSTED = "OUSTED"
    DISGRACE = "DISGRACE"

    @property
    def title(self) -> str:  # type: ignore[override]
        """Return the Chinese display title for the death reason."""

        match self:
            case DeathReason.BANKRUPTCY:
                return "破产清算"
            case DeathReason.MORALE_COLLAPSE:
                return "集体崩盘"
            case DeathReason.OUSTED:
                return "CEO 被罢免"
            case DeathReason.DISGRACE:
                return "身败名裂"


class StatsDelta(BaseModel):
    """Sparse stat changes produced by settlement."""

    model_config = ConfigDict(strict=True)

    CASH: int | None = None
    MORALE: int | None = None
    BOARD: int | None = None
    FACE: int | None = None

    def merge(self, other: StatsDelta) -> StatsDelta:
        """Return the field-wise sum of two sparse deltas."""

        return StatsDelta(
            CASH=_merge_value(self.CASH, other.CASH),
            MORALE=_merge_value(self.MORALE, other.MORALE),
            BOARD=_merge_value(self.BOARD, other.BOARD),
            FACE=_merge_value(self.FACE, other.FACE),
        )

    def as_dict(self) -> dict[str, int]:
        """Return only fields explicitly present on this delta."""

        values: dict[str, int] = {}
        if self.CASH is not None:
            values["CASH"] = self.CASH
        if self.MORALE is not None:
            values["MORALE"] = self.MORALE
        if self.BOARD is not None:
            values["BOARD"] = self.BOARD
        if self.FACE is not None:
            values["FACE"] = self.FACE
        return values


class Stats(BaseModel):
    """Immutable four-axis company health snapshot."""

    model_config = ConfigDict(frozen=True, strict=True)

    CASH: int = Field(ge=0, le=100)
    MORALE: int = Field(ge=0, le=100)
    BOARD: int = Field(ge=0, le=100)
    FACE: int = Field(ge=0, le=100)

    @classmethod
    def starting(cls, rng_seed: int | None = None, *, seed: int | None = None) -> Stats:
        """Build reproducible starting stats within v1 ranges."""

        rng = Random(seed if seed is not None else rng_seed)
        return cls(
            CASH=rng.randint(30, 60),
            MORALE=rng.randint(40, 60),
            BOARD=rng.randint(40, 60),
            FACE=rng.randint(50, 70),
        )

    def apply_delta(self, delta: StatsDelta) -> Stats:
        """Apply a sparse delta and clamp every stat to [0, 100]."""

        return type(self)(
            CASH=_clamp_stat(self.CASH + _delta_value(delta.CASH)),
            MORALE=_clamp_stat(self.MORALE + _delta_value(delta.MORALE)),
            BOARD=_clamp_stat(self.BOARD + _delta_value(delta.BOARD)),
            FACE=_clamp_stat(self.FACE + _delta_value(delta.FACE)),
        )

    def is_dead(self) -> DeathReason | None:
        """Return the first triggered death reason by DESIGN priority."""

        if self.CASH <= 0:
            return DeathReason.BANKRUPTCY
        if self.FACE <= 0:
            return DeathReason.DISGRACE
        if self.BOARD <= 5:
            return DeathReason.OUSTED
        if self.MORALE <= 10:
            return DeathReason.MORALE_COLLAPSE
        return None


def _merge_value(left: int | None, right: int | None) -> int | None:
    if left is None and right is None:
        return None
    return _delta_value(left) + _delta_value(right)


def _delta_value(value: int | None) -> int:
    return 0 if value is None else value


def _clamp_stat(value: int) -> int:
    return max(0, min(100, value))
