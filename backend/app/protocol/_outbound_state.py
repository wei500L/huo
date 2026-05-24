"""Stateful outbound DTOs converted from domain models."""

from __future__ import annotations

from typing import Literal

from pydantic import Field

from app.domain import DeathReason, GossipLead, HistoryEntry, LegacyUnlock, MetaProgress, Promise, Quarter

from ._outbound_base import OutboundBase
from ._outbound_core import (
    BriefingDTO,
    DecisionCardDTO,
    PressBundleDTO,
    PressInputDTO,
    SettlementDTO,
    StatsDTO,
)

__all__ = (
    "DeathReasonDTO",
    "GossipLeadDTO",
    "HistoryEntryDTO",
    "LastEmployeeDTO",
    "LegacyUnlockDTO",
    "MetaSummaryDTO",
    "PromiseDTO",
    "PromiseTargetDTO",
    "QuarterDTO",
)


class GossipLeadDTO(OutboundBase):
    id: str
    quarter: int
    scene: Literal["tearoom", "elevator", "meeting_room", "workstation", "rooftop", "smoking_area"]
    speaker_id: str | None = None
    text: str
    reliability: str
    linked_employee_ids: list[str] = Field(default_factory=list)
    ap_cost: int

    @classmethod
    def from_domain(cls, lead: GossipLead) -> GossipLeadDTO:
        data = lead.model_dump(exclude={"is_truth"})
        data["reliability"] = lead.reliability.value
        return cls.model_validate(data)


class DeathReasonDTO(OutboundBase):
    code: str
    label_zh: str

    @classmethod
    def from_domain(cls, reason: DeathReason) -> DeathReasonDTO:
        return cls(code=reason.value, label_zh=reason.title)


class LegacyUnlockDTO(OutboundBase):
    type: str
    label_zh: str
    description: str
    effect_summary: str
    earned_at_run_id: str
    earned_at_quarter: int

    @classmethod
    def from_domain(cls, unlock: LegacyUnlock) -> LegacyUnlockDTO:
        data = unlock.model_dump()
        data["type"] = unlock.type.value
        return cls.model_validate(data)


class LastEmployeeDTO(OutboundBase):
    name: str
    quote: str


class HistoryEntryDTO(OutboundBase):
    quarter: int
    decision_id: str
    press_bundle_id: str | None = None
    stats_before: StatsDTO
    stats_after: StatsDTO
    settlement_summary: str

    @classmethod
    def from_domain(cls, entry: HistoryEntry) -> HistoryEntryDTO:
        return cls(
            quarter=entry.quarter,
            decision_id=entry.decision_id,
            press_bundle_id=entry.press_bundle_id,
            stats_before=StatsDTO.from_domain(entry.stats_before),
            stats_after=StatsDTO.from_domain(entry.stats_after),
            settlement_summary=entry.settlement_summary,
        )


class QuarterDTO(OutboundBase):
    number: int
    phase: str
    briefing: BriefingDTO | None = None
    decision_cards: list[DecisionCardDTO] = Field(default_factory=list)
    selected_decision_id: str | None = None
    gossip_collected: list[str] = Field(default_factory=list)
    press_input: PressInputDTO | None = None
    press_bundle: PressBundleDTO | None = None
    settlement: SettlementDTO | None = None
    ap_remaining: int

    @classmethod
    def from_domain(cls, quarter: Quarter) -> QuarterDTO:
        return cls(
            number=quarter.number,
            phase=quarter.phase.value,
            briefing=(
                BriefingDTO.from_domain(quarter.briefing) if quarter.briefing is not None else None
            ),
            decision_cards=[DecisionCardDTO.from_domain(card) for card in quarter.decision_cards],
            selected_decision_id=quarter.selected_decision_id,
            gossip_collected=list(quarter.gossip_collected),
            press_input=(
                PressInputDTO.from_domain(quarter.press_input)
                if quarter.press_input is not None
                else None
            ),
            press_bundle=(
                PressBundleDTO.from_domain(quarter.press_bundle)
                if quarter.press_bundle is not None
                else None
            ),
            settlement=(
                SettlementDTO.from_domain(quarter.settlement)
                if quarter.settlement is not None
                else None
            ),
            ap_remaining=quarter.ap_remaining,
        )


class MetaSummaryDTO(OutboundBase):
    schema_version: int
    total_runs: int
    unlocked_legacies: list[LegacyUnlockDTO] = Field(default_factory=list)
    unlocked_styles: list[str] = Field(default_factory=list)
    death_log_count: int
    press_archive_count: int

    @classmethod
    def from_domain(cls, progress: MetaProgress) -> MetaSummaryDTO:
        return cls(
            schema_version=progress.schema_version,
            total_runs=progress.total_runs,
            unlocked_legacies=[
                LegacyUnlockDTO.from_domain(unlock) for unlock in progress.unlocked_legacies
            ],
            unlocked_styles=[style.value for style in progress.unlocked_styles],
            death_log_count=len(progress.death_log),
            press_archive_count=len(progress.press_archive),
        )


class PromiseTargetDTO(OutboundBase):
    metric: str
    target_expr: str
    deadline_quarter: int | None = None

    @classmethod
    def from_domain(cls, target: "Promise") -> PromiseTargetDTO:
        parsed = target.parsed
        if parsed is None:
            raise ValueError("Cannot convert None parsed target")
        return cls(
            metric=parsed.metric,
            target_expr=parsed.target_expr,
            deadline_quarter=parsed.deadline_quarter,
        )


class PromiseDTO(OutboundBase):
    id: str
    quarter_made: int
    source: str
    text: str
    fulfilled: bool | None = None
    judged_at_quarter: int | None = None
    parsed: PromiseTargetDTO | None = None

    @classmethod
    def from_domain(cls, promise: Promise) -> PromiseDTO:
        return cls(
            id=promise.id,
            quarter_made=promise.quarter_made,
            source=promise.source.value,
            text=promise.text,
            fulfilled=promise.fulfilled,
            judged_at_quarter=promise.judged_at_quarter,
            parsed=(
                PromiseTargetDTO(
                    metric=promise.parsed.metric,
                    target_expr=promise.parsed.target_expr,
                    deadline_quarter=promise.parsed.deadline_quarter,
                )
                if promise.parsed is not None
                else None
            ),
        )
