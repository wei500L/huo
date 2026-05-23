"""Press domain models."""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from .stats import StatsDelta

__all__ = (
    "MediaHeadline",
    "PressBundle",
    "PressEvaluation",
    "PressInput",
    "PressType",
)

PressScoreKey = Literal[
    "contentCompleteness",
    "issueResponse",
    "overpromise",
    "logicClarity",
    "confidence",
    "riskAvoidance",
    "memorableQuote",
    "weaknessExposed",
    "authenticity",
]


class PressType(StrEnum):
    """Press conference types."""

    INAUGURATION = "INAUGURATION"
    CRISIS = "CRISIS"
    PRODUCT = "PRODUCT"
    FINANCIAL = "FINANCIAL"
    ROADSHOW = "ROADSHOW"
    LAYOFF_EXPLAIN = "LAYOFF_EXPLAIN"
    REGULATOR = "REGULATOR"
    COUNTER = "COUNTER"

    @property
    def label_zh(self) -> str:
        """Return the Chinese display label."""

        match self:
            case PressType.INAUGURATION:
                return "就职"
            case PressType.CRISIS:
                return "危机回应"
            case PressType.PRODUCT:
                return "产品发布"
            case PressType.FINANCIAL:
                return "财务说明"
            case PressType.ROADSHOW:
                return "路演"
            case PressType.LAYOFF_EXPLAIN:
                return "裁员说明"
            case PressType.REGULATOR:
                return "监管沟通"
            case PressType.COUNTER:
                return "反击回应"


class PressInput(BaseModel):
    """Realtime transcript captured during a press conference."""

    model_config = ConfigDict(frozen=True, strict=True)

    quarter: int = Field(ge=1, le=4)
    press_type: PressType
    must_answer_topics: list[str] = Field(min_length=1, max_length=4)
    transcript: str = Field(min_length=30, max_length=600)
    duration_s: float | None = None
    word_count: int = Field(ge=0)
    flags: list[str] = Field(default_factory=list)
    submitted_at: datetime


class PressEvaluation(BaseModel):
    """Asynchronous LLM evaluation produced during settlement."""

    model_config = ConfigDict(strict=True)

    scores: dict[PressScoreKey, int] = Field(min_length=9, max_length=9)
    memorable_quote: str
    biggest_flaw: str
    media_angle: Literal["金句传播", "漏洞放大", "模糊带过"]
    stat_impact: StatsDelta

    @field_validator("scores")
    @classmethod
    def _validate_scores(cls, value: dict[PressScoreKey, int]) -> dict[PressScoreKey, int]:
        expected = {
            "contentCompleteness",
            "issueResponse",
            "overpromise",
            "logicClarity",
            "confidence",
            "riskAvoidance",
            "memorableQuote",
            "weaknessExposed",
            "authenticity",
        }
        if set(value) != expected:
            missing = sorted(expected - set(value))
            extra = sorted(set(value) - expected)
            raise ValueError(f"scores must contain exact keys; missing={missing}, extra={extra}")
        return value


class MediaHeadline(BaseModel):
    """A single media headline generated from a press evaluation."""

    model_config = ConfigDict(frozen=True, strict=True)

    outlet: Literal["36 氪", "彭博体", "晚点 LatePost", "虎嗅", "钛媒体", "脉脉自媒体"]
    headline: str = Field(max_length=22)
    tone: Literal["positive", "neutral", "negative", "mocking"]
    summary: str | None = Field(default=None, max_length=150)


class PressBundle(BaseModel):
    """Outbound settlement bundle for a completed press event."""

    model_config = ConfigDict(frozen=True, strict=True)

    input: PressInput
    evaluation: PressEvaluation
    headlines: list[MediaHeadline] = Field(min_length=1, max_length=4)
