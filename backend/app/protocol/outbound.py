"""Outbound protocol schema and DTO conversions."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel

from app.domain import (
    BoomerangSeed,
    BoardReaction,
    Briefing,
    Company,
    DeathCause,
    DeathLogEntry,
    DeathReason,
    DecisionCard,
    EmployeeGossip,
    GossipLead,
    HistoryEntry,
    LegacyUnlock,
    ManagementStyle,
    MetaProgress,
    MediaHeadline,
    PressBundle,
    PressEvaluation,
    PressInput,
    Quarter,
    RivalAction,
    Settlement,
    Stats,
    StatsDelta,
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


class _OutboundBase(BaseModel):
    model_config = ConfigDict(
        strict=True,
        extra="forbid",
        frozen=True,
        populate_by_name=True,
        alias_generator=to_camel,
    )


class StatsDTO(_OutboundBase):
    cash: int
    morale: int
    board: int
    face: int

    @classmethod
    def from_domain(cls, stats: Stats) -> StatsDTO:
        return cls(cash=stats.CASH, morale=stats.MORALE, board=stats.BOARD, face=stats.FACE)


class StatsDeltaDTO(_OutboundBase):
    cash: int | None = None
    morale: int | None = None
    board: int | None = None
    face: int | None = None

    @classmethod
    def from_domain(cls, delta: StatsDelta) -> StatsDeltaDTO:
        return cls(cash=delta.CASH, morale=delta.MORALE, board=delta.BOARD, face=delta.FACE)


class DeathCauseDTO(_OutboundBase):
    category: Literal["financial", "product", "org", "market", "capital", "trust", "absurd"]
    description: str

    @classmethod
    def from_domain(cls, cause: DeathCause) -> DeathCauseDTO:
        return cls(category=cause.category, description=cause.description)


class CompanyDTO(_OutboundBase):
    id: str
    name: str
    business: str
    absurdity: int
    founding_motto: str
    death_causes: list[DeathCauseDTO] = Field(default_factory=list)
    starting_promises: list[str] = Field(default_factory=list)
    founded_year: int

    @classmethod
    def from_domain(cls, company: Company) -> CompanyDTO:
        return cls(
            id=company.id,
            name=company.name,
            business=company.business,
            absurdity=company.absurdity,
            founding_motto=company.founding_motto,
            death_causes=[DeathCauseDTO.from_domain(item) for item in company.death_causes],
            starting_promises=list(company.starting_promises),
            founded_year=company.founded_year,
        )


class BoomerangSeedDTO(_OutboundBase):
    delay_quarters: Literal[1, 2, 3]
    probability: float
    description: str
    effect: StatsDeltaDTO

    @classmethod
    def from_domain(cls, seed: BoomerangSeed) -> BoomerangSeedDTO:
        return cls(
            delay_quarters=seed.delay_quarters,
            probability=seed.probability,
            description=seed.description,
            effect=StatsDeltaDTO.from_domain(seed.effect),
        )


class DecisionCardDTO(_OutboundBase):
    id: str
    category: str
    title: str
    description: str
    immediate_effect: StatsDeltaDTO
    flavor: str
    long_term_hint: str | None = None
    boomerang_seeds: list[BoomerangSeedDTO] = Field(default_factory=list)

    @classmethod
    def from_domain(cls, card: DecisionCard) -> DecisionCardDTO:
        return cls(
            id=card.id,
            category=card.category.value,
            title=card.title,
            description=card.description,
            immediate_effect=StatsDeltaDTO.from_domain(card.immediate_effect),
            flavor=card.flavor,
            long_term_hint=card.long_term_hint,
            boomerang_seeds=[BoomerangSeedDTO.from_domain(seed) for seed in card.boomerang_seeds],
        )


class BriefingDTO(_OutboundBase):
    quarter: int
    market_mood: Literal["bull", "neutral", "bear", "crisis"]
    headline_hint: str

    @classmethod
    def from_domain(cls, briefing: Briefing) -> BriefingDTO:
        data = briefing.model_dump(exclude={"hidden_risks"})
        return cls.model_validate(data)


class BoardReactionDTO(_OutboundBase):
    speech: str
    patience_delta: int
    vote: Literal["approve", "oppose", "abstain"]

    @classmethod
    def from_domain(cls, reaction: BoardReaction) -> BoardReactionDTO:
        return cls(
            speech=reaction.speech,
            patience_delta=reaction.patience_delta,
            vote=reaction.vote,
        )


class EmployeeGossipDTO(_OutboundBase):
    speaker: str
    line: str
    mood: Literal["anxious", "angry", "tired", "hopeful", "numb", "excited", "in_love"]

    @classmethod
    def from_domain(cls, gossip: EmployeeGossip) -> EmployeeGossipDTO:
        return cls(speaker=gossip.speaker, line=gossip.line, mood=gossip.mood)


class RivalActionDTO(_OutboundBase):
    rival_name: str
    action: Literal["price_war", "poach", "launch", "pr_attack", "wait", "acquisition_rumor"]
    description: str
    expected_damage: StatsDeltaDTO

    @classmethod
    def from_domain(cls, action: RivalAction) -> RivalActionDTO:
        return cls(
            rival_name=action.rival_name,
            action=action.action,
            description=action.description,
            expected_damage=StatsDeltaDTO.from_domain(action.expected_damage),
        )


class SettlementDTO(_OutboundBase):
    quarter: int
    quarter_report: str
    board_reaction: BoardReactionDTO
    employee_gossip: EmployeeGossipDTO
    rival_action: RivalActionDTO
    market_signal: Literal["bull", "neutral", "bear", "crisis"]
    metrics_delta: StatsDeltaDTO
    scheduled_events_added: list[str] = Field(default_factory=list)

    @classmethod
    def from_domain(cls, settlement: Settlement) -> SettlementDTO:
        return cls(
            quarter=settlement.quarter,
            quarter_report=settlement.quarter_report,
            board_reaction=BoardReactionDTO.from_domain(settlement.board_reaction),
            employee_gossip=EmployeeGossipDTO.from_domain(settlement.employee_gossip),
            rival_action=RivalActionDTO.from_domain(settlement.rival_action),
            market_signal=settlement.market_signal,
            metrics_delta=StatsDeltaDTO.from_domain(settlement.metrics_delta),
            scheduled_events_added=list(settlement.scheduled_events_added),
        )


class PressInputDTO(_OutboundBase):
    quarter: int
    press_type: str
    must_answer_topics: list[str]
    transcript: str
    duration_s: float | None = None
    word_count: int
    flags: list[str] = Field(default_factory=list)
    submitted_at: datetime

    @classmethod
    def from_domain(cls, press_input: PressInput) -> PressInputDTO:
        data = press_input.model_dump()
        data["press_type"] = press_input.press_type.value
        return cls.model_validate(data)


class PressEvaluationDTO(_OutboundBase):
    scores: dict[str, int]
    memorable_quote: str
    biggest_flaw: str
    media_angle: Literal["金句传播", "漏洞放大", "模糊带过"]
    stat_impact: StatsDeltaDTO

    @classmethod
    def from_domain(cls, evaluation: PressEvaluation) -> PressEvaluationDTO:
        data = evaluation.model_dump(exclude={"internal_eval"})
        data["stat_impact"] = StatsDeltaDTO.from_domain(evaluation.stat_impact)
        return cls.model_validate(data)


class MediaHeadlineDTO(_OutboundBase):
    outlet: Literal["36 氪", "彭博体", "晚点 LatePost", "虎嗅", "钛媒体", "脉脉自媒体"]
    headline: str
    tone: Literal["positive", "neutral", "negative", "mocking"]
    summary: str | None = None

    @classmethod
    def from_domain(cls, headline: MediaHeadline) -> MediaHeadlineDTO:
        return cls(
            outlet=headline.outlet,
            headline=headline.headline,
            tone=headline.tone,
            summary=headline.summary,
        )


class PressBundleDTO(_OutboundBase):
    input: PressInputDTO
    evaluation: PressEvaluationDTO
    headlines: list[MediaHeadlineDTO]

    @classmethod
    def from_domain(cls, bundle: PressBundle) -> PressBundleDTO:
        return cls(
            input=PressInputDTO.from_domain(bundle.input),
            evaluation=PressEvaluationDTO.from_domain(bundle.evaluation),
            headlines=[MediaHeadlineDTO.from_domain(headline) for headline in bundle.headlines],
        )


class GossipLeadDTO(_OutboundBase):
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


class DeathReasonDTO(_OutboundBase):
    code: str
    label_zh: str

    @classmethod
    def from_domain(cls, reason: DeathReason) -> DeathReasonDTO:
        return cls(code=reason.value, label_zh=reason.title)


class LegacyUnlockDTO(_OutboundBase):
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


class LastEmployeeDTO(_OutboundBase):
    name: str
    quote: str


class HistoryEntryDTO(_OutboundBase):
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


class QuarterDTO(_OutboundBase):
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


class MetaSummaryDTO(_OutboundBase):
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


class GameSnapshot(_OutboundBase):
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


class DecisionAck(_OutboundBase):
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


class GossipResult(_OutboundBase):
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


class PressAck(_OutboundBase):
    session_id: str
    quarter_number: int
    accepted: bool
    flags: list[str] = Field(default_factory=list)
    replaced_count: int = 0


class SettlementBundle(_OutboundBase):
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


class LastEmployeeQuoteDTO(_OutboundBase):
    name: str
    quote: str


class DeathReportBundle(_OutboundBase):
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


class Toast(_OutboundBase):
    level: Literal["info", "warn", "error"]
    message: str
    hint: str | None = None


class ErrorOutbound(_OutboundBase):
    code: str
    message: str
    retryable: bool
