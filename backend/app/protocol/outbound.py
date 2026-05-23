"""Outbound protocol schema and public exports."""

from __future__ import annotations

from typing import Literal

from pydantic import Field

from app.domain import (
    Company,
    DeathLogEntry,
    DeathReason,
    GossipLead,
    HistoryEntry,
    LegacyUnlock,
    ManagementStyle,
    MetaProgress,
    PressBundle,
    Quarter,
    Settlement,
    Stats,
)

from ._outbound_base import OutboundBase
from ._outbound_core import (
    BoardReactionDTO,
    BoomerangSeedDTO,
    BriefingDTO,
    CompanyDTO,
    DeathCauseDTO,
    DecisionCardDTO,
    EmployeeGossipDTO,
    MediaHeadlineDTO,
    PressBundleDTO,
    PressEvaluationDTO,
    PressInputDTO,
    RivalActionDTO,
    SettlementDTO,
    StatsDeltaDTO,
    StatsDTO,
)
from ._outbound_state import (
    DeathReasonDTO,
    GossipLeadDTO,
    HistoryEntryDTO,
    LastEmployeeDTO,
    LegacyUnlockDTO,
    MetaSummaryDTO,
    QuarterDTO,
)

__all__ = (
    "BoardReactionDTO",
    "BoomerangSeedDTO",
    "BriefingDTO",
    "CompanyDTO",
    "DeathCauseDTO",
    "DeathReasonDTO",
    "DeathReportBundle",
    "DecisionAck",
    "DecisionCardDTO",
    "EmployeeGossipDTO",
    "ErrorOutbound",
    "GameSnapshot",
    "GossipLeadDTO",
    "GossipResult",
    "HistoryEntryDTO",
    "LastEmployeeDTO",
    "LegacyUnlockDTO",
    "MediaHeadlineDTO",
    "MetaSummaryDTO",
    "PressAck",
    "PressBundleDTO",
    "PressEvaluationDTO",
    "PressInputDTO",
    "QuarterDTO",
    "RivalActionDTO",
    "SettlementBundle",
    "SettlementDTO",
    "StatsDTO",
    "StatsDeltaDTO",
    "Toast",
)


class GameSnapshot(OutboundBase):
    session_id: str
    player_id: str
    company: CompanyDTO
    stats: StatsDTO
    quarter: QuarterDTO
    history: list[HistoryEntryDTO] = Field(default_factory=list)
    meta_summary: MetaSummaryDTO

    @classmethod
    def from_domain(
        cls,
        *,
        session_id: str,
        player_id: str,
        company: Company,
        stats: Stats,
        quarter: Quarter,
        history: list[HistoryEntry],
        meta_progress: MetaProgress,
    ) -> GameSnapshot:
        return cls(
            session_id=session_id,
            player_id=player_id,
            company=CompanyDTO.from_domain(company),
            stats=StatsDTO.from_domain(stats),
            quarter=QuarterDTO.from_domain(quarter),
            history=[HistoryEntryDTO.from_domain(entry) for entry in history],
            meta_summary=MetaSummaryDTO.from_domain(meta_progress),
        )


class DecisionAck(OutboundBase):
    session_id: str
    quarter_number: int
    card_id: str
    immediate_stats: StatsDTO
    next_phase: Literal["GOSSIP", "DECISION", "PRESS", "SETTLEMENT", "DONE"]

    @classmethod
    def from_domain(
        cls,
        *,
        session_id: str,
        quarter_number: int,
        card_id: str,
        immediate_stats: Stats,
        next_phase: Literal["GOSSIP", "DECISION", "PRESS", "SETTLEMENT", "DONE"],
    ) -> DecisionAck:
        return cls(
            session_id=session_id,
            quarter_number=quarter_number,
            card_id=card_id,
            immediate_stats=StatsDTO.from_domain(immediate_stats),
            next_phase=next_phase,
        )


class GossipResult(OutboundBase):
    session_id: str
    quarter_number: int
    lead: GossipLeadDTO
    ap_remaining: int

    @classmethod
    def from_domain(
        cls,
        *,
        session_id: str,
        quarter_number: int,
        lead: GossipLead,
        ap_remaining: int,
    ) -> GossipResult:
        return cls(
            session_id=session_id,
            quarter_number=quarter_number,
            lead=GossipLeadDTO.from_domain(lead),
            ap_remaining=ap_remaining,
        )


class PressAck(OutboundBase):
    session_id: str
    quarter_number: int
    accepted: bool
    flags: list[str] = Field(default_factory=list)
    replaced_count: int = 0


class SettlementBundle(OutboundBase):
    session_id: str
    quarter_number: int
    settlement: SettlementDTO
    press_bundle: PressBundleDTO | None = None
    new_stats: StatsDTO
    history_added: HistoryEntryDTO
    death: DeathReasonDTO | None = None

    @classmethod
    def from_domain(
        cls,
        *,
        session_id: str,
        quarter_number: int,
        settlement: Settlement,
        press_bundle: PressBundle | None,
        new_stats: Stats,
        history_added: HistoryEntry,
        death: DeathReason | None,
    ) -> SettlementBundle:
        return cls(
            session_id=session_id,
            quarter_number=quarter_number,
            settlement=SettlementDTO.from_domain(settlement),
            press_bundle=(
                PressBundleDTO.from_domain(press_bundle) if press_bundle is not None else None
            ),
            new_stats=StatsDTO.from_domain(new_stats),
            history_added=HistoryEntryDTO.from_domain(history_added),
            death=DeathReasonDTO.from_domain(death) if death is not None else None,
        )


class DeathReportBundle(OutboundBase):
    session_id: str
    obituary: str
    biggest_mistake_decision_id: str | None
    last_employee: LastEmployeeDTO | None = None
    headlines: list[str] = Field(default_factory=list)
    legacy_unlocks: list[LegacyUnlockDTO] = Field(default_factory=list)
    styles_unlocked: list[str] = Field(default_factory=list)

    @classmethod
    def from_domain(
        cls,
        *,
        session_id: str,
        death_log_entry: DeathLogEntry,
        legacy_unlocks: list[LegacyUnlock],
        styles_unlocked: list[ManagementStyle],
        last_employee_name: str | None,
        last_employee_quote: str | None,
    ) -> DeathReportBundle:
        last_employee = None
        if last_employee_name is not None and last_employee_quote is not None:
            last_employee = LastEmployeeDTO(name=last_employee_name, quote=last_employee_quote)
        return cls(
            session_id=session_id,
            obituary=death_log_entry.obituary,
            biggest_mistake_decision_id=death_log_entry.biggest_mistake_decision_id,
            last_employee=last_employee,
            headlines=list(death_log_entry.headlines),
            legacy_unlocks=[LegacyUnlockDTO.from_domain(unlock) for unlock in legacy_unlocks],
            styles_unlocked=[style.value for style in styles_unlocked],
        )


class Toast(OutboundBase):
    level: Literal["info", "warn", "error"]
    message: str
    hint: str | None = None


class ErrorOutbound(OutboundBase):
    code: str
    message: str
    retryable: bool
