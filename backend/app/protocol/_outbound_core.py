"""Core outbound DTOs converted from domain models."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import Field

from app.domain import (
    BoardReaction,
    BoomerangSeed,
    Briefing,
    Company,
    DeathCause,
    DecisionCard,
    EmployeeGossip,
    MediaHeadline,
    PressBundle,
    PressEvaluation,
    PressInput,
    RivalAction,
    Settlement,
    Stats,
    StatsDelta,
)

from ._outbound_base import OutboundBase

__all__ = (
    "BoardReactionDTO",
    "BoomerangSeedDTO",
    "BriefingDTO",
    "CompanyDTO",
    "DeathCauseDTO",
    "DecisionCardDTO",
    "EmployeeGossipDTO",
    "MediaHeadlineDTO",
    "PressBundleDTO",
    "PressEvaluationDTO",
    "PressInputDTO",
    "RivalActionDTO",
    "SettlementDTO",
    "StatsDTO",
    "StatsDeltaDTO",
)


class StatsDTO(OutboundBase):
    cash: int
    morale: int
    board: int
    face: int

    @classmethod
    def from_domain(cls, stats: Stats) -> StatsDTO:
        return cls(cash=stats.CASH, morale=stats.MORALE, board=stats.BOARD, face=stats.FACE)


class StatsDeltaDTO(OutboundBase):
    cash: int | None = None
    morale: int | None = None
    board: int | None = None
    face: int | None = None

    @classmethod
    def from_domain(cls, delta: StatsDelta) -> StatsDeltaDTO:
        return cls(cash=delta.CASH, morale=delta.MORALE, board=delta.BOARD, face=delta.FACE)


class DeathCauseDTO(OutboundBase):
    category: Literal["financial", "product", "org", "market", "capital", "trust", "absurd"]
    description: str

    @classmethod
    def from_domain(cls, cause: DeathCause) -> DeathCauseDTO:
        return cls(category=cause.category, description=cause.description)


class CompanyDTO(OutboundBase):
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


class BoomerangSeedDTO(OutboundBase):
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


class DecisionCardDTO(OutboundBase):
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


class BriefingDTO(OutboundBase):
    quarter: int
    market_mood: Literal["bull", "neutral", "bear", "crisis"]
    headline_hint: str

    @classmethod
    def from_domain(cls, briefing: Briefing) -> BriefingDTO:
        data = briefing.model_dump(exclude={"hidden_risks"})
        return cls.model_validate(data)


class BoardReactionDTO(OutboundBase):
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


class EmployeeGossipDTO(OutboundBase):
    speaker: str
    line: str
    mood: Literal["anxious", "angry", "tired", "hopeful", "numb", "excited", "in_love"]

    @classmethod
    def from_domain(cls, gossip: EmployeeGossip) -> EmployeeGossipDTO:
        return cls(speaker=gossip.speaker, line=gossip.line, mood=gossip.mood)


class RivalActionDTO(OutboundBase):
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


class SettlementDTO(OutboundBase):
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


class PressInputDTO(OutboundBase):
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


class PressEvaluationDTO(OutboundBase):
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


class MediaHeadlineDTO(OutboundBase):
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


class PressBundleDTO(OutboundBase):
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
