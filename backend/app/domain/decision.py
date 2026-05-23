"""Decision domain models."""

from __future__ import annotations

from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from .stats import StatsDelta

__all__ = ("BoomerangSeed", "DecisionCard", "DecisionCategory")


class DecisionCategory(StrEnum):
    """Decision card categories."""

    FUNDING = "FUNDING"
    LAYOFF = "LAYOFF"
    SELL_ASSET = "SELL_ASSET"
    PIVOT = "PIVOT"
    KILL_PRODUCT = "KILL_PRODUCT"
    PRICE_WAR = "PRICE_WAR"
    SOOTHE = "SOOTHE"
    SWAP_EXEC = "SWAP_EXEC"
    HIDE_BAD_NEWS = "HIDE_BAD_NEWS"
    DELAY_BOARD = "DELAY_BOARD"
    NEGOTIATE_RIVAL = "NEGOTIATE_RIVAL"
    HUMILIATING_TERM = "HUMILIATING_TERM"

    @property
    def label_zh(self) -> str:
        """Return the Chinese display label."""

        match self:
            case DecisionCategory.FUNDING:
                return "融资"
            case DecisionCategory.LAYOFF:
                return "裁员"
            case DecisionCategory.SELL_ASSET:
                return "卖资产"
            case DecisionCategory.PIVOT:
                return "产品转型"
            case DecisionCategory.KILL_PRODUCT:
                return "砍产品线"
            case DecisionCategory.PRICE_WAR:
                return "价格战"
            case DecisionCategory.SOOTHE:
                return "安抚员工"
            case DecisionCategory.SWAP_EXEC:
                return "换高管"
            case DecisionCategory.HIDE_BAD_NEWS:
                return "隐瞒坏消息"
            case DecisionCategory.DELAY_BOARD:
                return "争取董事会时间"
            case DecisionCategory.NEGOTIATE_RIVAL:
                return "与对手谈判"
            case DecisionCategory.HUMILIATING_TERM:
                return "接受屈辱条款"


class BoomerangSeed(BaseModel):
    """Delayed adverse effect emitted by a decision card."""

    model_config = ConfigDict(frozen=True, strict=True)

    delay_quarters: Literal[1, 2, 3]
    probability: float = Field(ge=0, le=1)
    description: str = Field(max_length=40)
    effect: StatsDelta

    @field_validator("effect")
    @classmethod
    def _validate_effect_bounds(cls, value: StatsDelta) -> StatsDelta:
        _validate_stats_delta_bounds(value)
        return value


class DecisionCard(BaseModel):
    """A bad option presented to the player in a quarter."""

    model_config = ConfigDict(frozen=True, strict=True)

    id: str
    category: DecisionCategory
    title: str = Field(max_length=14)
    description: str = Field(max_length=40)
    immediate_effect: StatsDelta
    flavor: str = Field(max_length=30)
    long_term_hint: str | None = Field(default=None, max_length=30)
    boomerang_seeds: list[BoomerangSeed] = Field(default_factory=list)

    @field_validator("immediate_effect")
    @classmethod
    def _validate_immediate_effect_bounds(cls, value: StatsDelta) -> StatsDelta:
        _validate_stats_delta_bounds(value)
        return value


def _validate_stats_delta_bounds(delta: StatsDelta) -> None:
    for field_name, value in delta.model_dump(exclude_none=True).items():
        if value < -25 or value > 25:
            raise ValueError(f"{field_name} must be between -25 and 25")
