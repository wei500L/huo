"""Strict raw-output schemas for LLM payloads."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

MetricKey = Literal["CASH", "MORALE", "BOARD", "FACE"]
MarketSignal = Literal["bull", "neutral", "bear", "crisis"]
Vote = Literal["approve", "oppose", "abstain"]
GossipMood = Literal[
    "anxious",
    "angry",
    "tired",
    "hopeful",
    "numb",
    "excited",
    "in_love",
    "neutral",
]
MediaTone = Literal["positive", "neutral", "negative", "mocking"]
RivalMove = Literal["price_war", "poach", "launch", "pr_attack", "wait", "acquisition_rumor"]
ScoreKey = Literal[
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
MediaAngle = Literal["金句传播", "漏洞放大", "模糊带过"]

METRIC_KEYS: tuple[str, ...] = ("CASH", "MORALE", "BOARD", "FACE")
SCORE_KEYS: tuple[str, ...] = (
    "contentCompleteness",
    "issueResponse",
    "overpromise",
    "logicClarity",
    "confidence",
    "riskAvoidance",
    "memorableQuote",
    "weaknessExposed",
    "authenticity",
)


class _RawBase(BaseModel):
    model_config = ConfigDict(strict=True, extra="ignore")


def _validate_metric_delta(value: dict[MetricKey, int]) -> dict[MetricKey, int]:
    if set(value) != set(METRIC_KEYS):
        raise ValueError("metric delta must contain exactly CASH, MORALE, BOARD, FACE")
    if any(item < -15 or item > 10 for item in value.values()):
        raise ValueError("metric delta values must be between -15 and 10")
    return value


class BoardReactionRaw(_RawBase):
    speech: str = Field(max_length=80)
    patienceDelta: int = Field(ge=-2, le=1)
    vote: Vote = "abstain"


class EmployeeGossipRaw(_RawBase):
    speaker: str = Field(max_length=12)
    line: str = Field(max_length=50)
    mood: GossipMood = "neutral"


class MediaHeadlineRaw(_RawBase):
    outlet: str
    headline: str = Field(max_length=30)
    tone: MediaTone


class RivalActionRaw(_RawBase):
    rival: str = Field(max_length=20)
    action: RivalMove
    move: str = Field(max_length=60)
    expectedDamage: dict[MetricKey, int]

    @field_validator("expectedDamage")
    @classmethod
    def _expected_damage_keys(cls, value: dict[MetricKey, int]) -> dict[MetricKey, int]:
        return _validate_metric_delta(value)


class DirectorRaw(_RawBase):
    boardReaction: BoardReactionRaw
    employeeGossip: EmployeeGossipRaw
    mediaHeadline: MediaHeadlineRaw
    rivalAction: RivalActionRaw
    marketSignal: MarketSignal
    metricsDelta: dict[MetricKey, int]
    quarterReport: str = Field(min_length=40, max_length=200)

    @field_validator("metricsDelta")
    @classmethod
    def _metrics_delta_keys(cls, value: dict[MetricKey, int]) -> dict[MetricKey, int]:
        return _validate_metric_delta(value)


class PressEvalRaw(_RawBase):
    scores: dict[ScoreKey, int]
    memorableQuote: str = Field(max_length=80)
    biggestFlaw: str = Field(max_length=120)
    mediaAngle: MediaAngle
    metricsDelta: dict[MetricKey, int]
    internalEval: str = Field(
        max_length=200,
        default="",
        description="WARN: backend-only diagnostic field; never include in outbound DTOs.",
    )

    @field_validator("scores")
    @classmethod
    def _score_keys(cls, value: dict[ScoreKey, int]) -> dict[ScoreKey, int]:
        if set(value) != set(SCORE_KEYS):
            raise ValueError("scores must contain exactly the nine press score keys")
        if any(item < 0 or item > 100 for item in value.values()):
            raise ValueError("score values must be between 0 and 100")
        return value

    @field_validator("metricsDelta")
    @classmethod
    def _metrics_delta_keys(cls, value: dict[MetricKey, int]) -> dict[MetricKey, int]:
        return _validate_metric_delta(value)


class DeathReportRaw(_RawBase):
    obituary: str = Field(min_length=200, max_length=600)
    biggestMistakeDecisionId: str | None
    lastEmployee: dict[str, Any] | None
    headlines: list[str] = Field(min_length=3, max_length=3)
    legacyUnlocks: list[str]


__all__ = (
    "BoardReactionRaw",
    "DeathReportRaw",
    "DirectorRaw",
    "EmployeeGossipRaw",
    "METRIC_KEYS",
    "MediaHeadlineRaw",
    "PressEvalRaw",
    "RivalActionRaw",
    "SCORE_KEYS",
)
