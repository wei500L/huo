"""Promise domain models."""

from __future__ import annotations

from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

__all__ = ("Promise", "PromiseSource", "PromiseTarget")


class PromiseSource(StrEnum):
    """Where a promise was made."""

    PRESS = "PRESS"
    BOARD_QA = "BOARD_QA"
    DECISION_FLAVOR = "DECISION_FLAVOR"
    FREE_TEXT = "FREE_TEXT"


class PromiseTarget(BaseModel):
    """Parsed promise target from a player statement."""

    model_config = ConfigDict(strict=True)

    metric: Literal["CASH", "MORALE", "BOARD", "FACE", "SALES_HINT"]
    target_expr: str
    deadline_quarter: int | None = Field(default=None, ge=1, le=4)


class Promise(BaseModel):
    """A promise recorded during the current run."""

    model_config = ConfigDict(strict=True)

    id: str
    quarter_made: int = Field(ge=1, le=4)
    source: PromiseSource
    text: str = Field(max_length=80)
    parsed: PromiseTarget | None = None
    fulfilled: bool | None = None
    judged_at_quarter: int | None = Field(default=None, ge=1, le=4)
