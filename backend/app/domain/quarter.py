"""Quarter domain models."""

from __future__ import annotations

from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from .decision import DecisionCard
from .press import PressBundle, PressInput
from .stats import Stats, StatsDelta

__all__ = (
    "BoardReaction",
    "Briefing",
    "EmployeeGossip",
    "HistoryEntry",
    "Quarter",
    "QuarterPhase",
    "RivalAction",
    "Settlement",
)


class QuarterPhase(StrEnum):
    """Quarter lifecycle phase."""

    BRIEFING = "BRIEFING"
    GOSSIP = "GOSSIP"
    DECISION = "DECISION"
    PRESS = "PRESS"
    SETTLEMENT = "SETTLEMENT"
    DONE = "DONE"


class Briefing(BaseModel):
    """Quarter briefing packet."""

    model_config = ConfigDict(frozen=True, strict=True)

    quarter: int = Field(ge=1, le=4)
    market_mood: Literal["bull", "neutral", "bear", "crisis"]
    headline_hint: str = Field(max_length=60)
    hidden_risks: list[str] = Field(
        default_factory=list,
        description="WARN: backend-only, do not include in outbound payloads",
    )


class BoardReaction(BaseModel):
    """Board reaction emitted during settlement."""

    model_config = ConfigDict(frozen=True, strict=True)

    speech: str = Field(max_length=60)
    patience_delta: int = Field(ge=-2, le=1)
    vote: Literal["approve", "oppose", "abstain"]


class EmployeeGossip(BaseModel):
    """Employee gossip emitted during settlement."""

    model_config = ConfigDict(frozen=True, strict=True)

    speaker: str = Field(max_length=6)
    line: str = Field(max_length=35)
    mood: Literal["anxious", "angry", "tired", "hopeful", "numb", "excited", "in_love"]


class RivalAction(BaseModel):
    """Rival response emitted during settlement."""

    model_config = ConfigDict(frozen=True, strict=True)

    rival_name: str
    action: Literal["price_war", "poach", "launch", "pr_attack", "wait", "acquisition_rumor"]
    description: str = Field(max_length=60)
    expected_damage: StatsDelta


class Settlement(BaseModel):
    """Quarter settlement snapshot."""

    model_config = ConfigDict(strict=True)

    quarter: int = Field(ge=1, le=4)
    quarter_report: str = Field(min_length=80, max_length=150)
    board_reaction: BoardReaction
    employee_gossip: EmployeeGossip
    rival_action: RivalAction
    market_signal: Literal["bull", "neutral", "bear", "crisis"]
    metrics_delta: StatsDelta
    scheduled_events_added: list[str] = Field(default_factory=list)


class Quarter(BaseModel):
    """Mutable quarter state used by the state machine."""

    model_config = ConfigDict(strict=True)

    number: int = Field(ge=1, le=4)
    phase: QuarterPhase = QuarterPhase.BRIEFING
    briefing: Briefing | None = None
    decision_cards: list[DecisionCard] = Field(default_factory=list)
    selected_decision_id: str | None = None
    gossip_collected: list[str] = Field(default_factory=list)
    press_input: PressInput | None = None
    press_bundle: PressBundle | None = None
    settlement: Settlement | None = None
    ap_remaining: int = Field(ge=0, default=10)


class HistoryEntry(BaseModel):
    """Historical record of a resolved quarter."""

    model_config = ConfigDict(frozen=True, strict=True)

    quarter: int = Field(ge=1, le=4)
    decision_id: str
    press_bundle_id: str | None = None
    stats_before: Stats
    stats_after: Stats
    settlement_summary: str = Field(max_length=60)
