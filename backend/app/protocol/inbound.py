"""Inbound protocol schema."""

from __future__ import annotations

from datetime import datetime
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel

__all__ = (
    "CollectGossip",
    "CreateGame",
    "DrawDecisions",
    "InboundMessage",
    "Ping",
    "RequestSnapshot",
    "SelectDecision",
    "SettleQuarter",
    "StateTransition",
    "SubmitPress",
)


class _InboundBase(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid", populate_by_name=True, alias_generator=to_camel)


class CreateGame(_InboundBase):
    type: Literal["create_game"] = "create_game"
    player_id: str | None = None
    request_legacies: bool = True
    company_template_id: str | None = None


class StateTransition(_InboundBase):
    type: Literal["state_transition"] = "state_transition"
    session_id: str
    target_phase: Literal["GOSSIP", "DECISION", "PRESS", "SETTLEMENT", "DONE"]


class DrawDecisions(_InboundBase):
    type: Literal["draw_decisions"] = "draw_decisions"
    session_id: str
    quarter_number: int = Field(ge=1, le=4)


class SelectDecision(_InboundBase):
    type: Literal["select_decision"] = "select_decision"
    session_id: str
    quarter_number: int = Field(ge=1, le=4)
    card_id: str


class CollectGossip(_InboundBase):
    type: Literal["collect_gossip"] = "collect_gossip"
    session_id: str
    quarter_number: int
    scene: Literal["tearoom", "elevator", "meeting_room", "workstation", "rooftop", "smoking_area"]


class SubmitPress(_InboundBase):
    type: Literal["submit_press"] = "submit_press"
    session_id: str
    quarter_number: int = 3
    press_type: Literal[
        "INAUGURATION",
        "CRISIS",
        "PRODUCT",
        "FINANCIAL",
        "ROADSHOW",
        "LAYOFF_EXPLAIN",
        "REGULATOR",
        "COUNTER",
    ]
    transcript: str = Field(min_length=30, max_length=600)
    duration_s: float | None = None


class SettleQuarter(_InboundBase):
    type: Literal["settle_quarter"] = "settle_quarter"
    session_id: str
    quarter_number: int = Field(ge=1, le=4)


class RequestSnapshot(_InboundBase):
    type: Literal["request_snapshot"] = "request_snapshot"
    session_id: str


class Ping(_InboundBase):
    type: Literal["ping"] = "ping"
    sent_at: datetime


InboundMessage = Annotated[
    CreateGame
    | StateTransition
    | DrawDecisions
    | SelectDecision
    | CollectGossip
    | SubmitPress
    | SettleQuarter
    | RequestSnapshot
    | Ping,
    Field(discriminator="type"),
]
