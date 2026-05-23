"""Director rule resolver."""

from __future__ import annotations

import logging
import re
from typing import Literal, cast

from pydantic import BaseModel, ConfigDict, Field

from app.domain import (
    BoardReaction,
    EmployeeGossip,
    MemoryActor,
    MemoryEntry,
    Promise,
    RivalAction,
    ScheduledEvent,
    Settlement,
    Stats,
    StatsDelta,
)
from app.llm.schema import DirectorRaw
from app.services.settlement_aggregator import SettlementContext

from ._utils import (
    LEGACY_BUFF_TABLE,
    build_stable_id,
    clamp_int,
    clamp_text,
    legacy_buff_delta,
    merge_stats_deltas,
    normalize_action,
    normalize_choice,
    normalize_mood,
    normalize_outlet,
    normalize_vote,
    stats_delta_from_mapping,
)

logger = logging.getLogger(__name__)


class PromiseJudgement(BaseModel):
    """Compatibility model for legacy callers."""

    model_config = ConfigDict(frozen=True, strict=True)

    promise_id: str
    fulfilled: bool
    judged_at_quarter: int = Field(ge=1, le=4)


class DirectorResolveResult(BaseModel):
    """Final authority result produced from director raw output."""

    model_config = ConfigDict(frozen=True, strict=True)

    settlement: Settlement
    new_scheduled_events: list[ScheduledEvent] = Field(default_factory=list)
    new_memory_entries: list[MemoryEntry] = Field(default_factory=list)
    promise_judgement: list[tuple[str, bool]] = Field(default_factory=list)


DirectorResolution = DirectorResolveResult


class DirectorResolver:
    """Turn validated director raw output into authoritative settlement."""

    def __init__(self) -> None:
        self.legacy_buff_table = dict(LEGACY_BUFF_TABLE)

    def resolve(self, ctx: SettlementContext, raw: DirectorRaw) -> DirectorResolveResult:
        raw_metrics_delta = stats_delta_from_mapping(
            {key: clamp_int(value, -15, 10) for key, value in raw.metricsDelta.items()}
        )

        promise_judgement: list[tuple[str, bool]] = []
        for promise in ctx.active_promises:
            fulfilled = _judge_promise(promise, ctx)
            if fulfilled is not None:
                promise_judgement.append((promise.id, fulfilled))

        promise_adjustment_delta = StatsDelta(
            CASH=0,
            MORALE=0,
            BOARD=5 * sum(1 for _, fulfilled in promise_judgement if fulfilled)
            - 8 * sum(1 for _, fulfilled in promise_judgement if not fulfilled),
            FACE=0,
        )
        scheduled_firing_delta = merge_stats_deltas(
            *(event.effect_on_fire for event in ctx.scheduled_events_firing_this_quarter)
        )
        legacy_adjustment_delta = legacy_buff_delta(ctx.meta_buff_signature, raw_metrics_delta)
        total_delta = merge_stats_deltas(
            raw_metrics_delta,
            promise_adjustment_delta,
            scheduled_firing_delta,
            legacy_adjustment_delta,
        )

        settlement = Settlement(
            quarter=ctx.quarter_number,
            quarter_report=_fit_quarter_report(
                raw.quarterReport,
                raw.boardReaction.speech,
                raw.employeeGossip.line,
                raw.mediaHeadline.headline,
                raw.rivalAction.move,
            ),
            board_reaction=BoardReaction(
                speech=clamp_text(raw.boardReaction.speech, 60),
                patience_delta=clamp_int(raw.boardReaction.patienceDelta, -2, 1),
                vote=cast(
                    Literal["approve", "oppose", "abstain"],
                    normalize_vote(raw.boardReaction.vote),
                ),
            ),
            employee_gossip=EmployeeGossip(
                speaker=clamp_text(raw.employeeGossip.speaker, 6),
                line=clamp_text(raw.employeeGossip.line, 35),
                mood=cast(
                    Literal["anxious", "angry", "tired", "hopeful", "numb", "excited", "in_love"],
                    normalize_mood(raw.employeeGossip.mood),
                ),
            ),
            rival_action=RivalAction(
                rival_name=clamp_text(raw.rivalAction.rival, 20),
                action=cast(
                    Literal[
                        "price_war",
                        "poach",
                        "launch",
                        "pr_attack",
                        "wait",
                        "acquisition_rumor",
                    ],
                    normalize_action(raw.rivalAction.action),
                ),
                description=clamp_text(raw.rivalAction.move, 60),
                expected_damage=stats_delta_from_mapping(
                    {
                        key: clamp_int(value, -15, 10)
                        for key, value in raw.rivalAction.expectedDamage.items()
                    }
                ),
            ),
            market_signal=cast(
                Literal["bull", "neutral", "bear", "crisis"],
                normalize_choice(
                    raw.marketSignal,
                    ("bull", "neutral", "bear", "crisis"),
                    fallback="neutral",
                    kind="market_signal",
                ),
            ),
            metrics_delta=total_delta,
            scheduled_events_added=[],
        )

        new_memory_entries = [
            MemoryEntry(
                id=build_stable_id(
                    ctx.session_id, ctx.quarter_number, "BOARD", raw.boardReaction.speech
                ),
                actor=MemoryActor.BOARD,
                actor_id="BOARD",
                quarter=ctx.quarter_number,
                event_type="decision_seen",
                summary=clamp_text(raw.boardReaction.speech, 60),
                weight=4,
            ),
            MemoryEntry(
                id=build_stable_id(
                    ctx.session_id, ctx.quarter_number, "EMPLOYEE", raw.employeeGossip.speaker
                ),
                actor=MemoryActor.EMPLOYEE,
                actor_id=clamp_text(raw.employeeGossip.speaker, 12),
                quarter=ctx.quarter_number,
                event_type=_employee_event_type(raw.employeeGossip.mood),
                summary=clamp_text(raw.employeeGossip.line, 80),
                weight=3,
            ),
            MemoryEntry(
                id=build_stable_id(
                    ctx.session_id, ctx.quarter_number, "MEDIA", raw.mediaHeadline.outlet
                ),
                actor=MemoryActor.MEDIA,
                actor_id=normalize_outlet(raw.mediaHeadline.outlet),
                quarter=ctx.quarter_number,
                event_type="press_quote",
                summary=clamp_text(
                    f"{normalize_outlet(raw.mediaHeadline.outlet)} {raw.mediaHeadline.headline}",
                    80,
                ),
                weight=3,
            ),
        ]

        return DirectorResolveResult(
            settlement=settlement,
            new_scheduled_events=[],
            new_memory_entries=new_memory_entries,
            promise_judgement=promise_judgement,
        )


def _judge_promise(promise: Promise, ctx: SettlementContext) -> bool | None:
    parsed = promise.parsed
    if parsed is None or parsed.deadline_quarter is None:
        return None
    if parsed.deadline_quarter > ctx.quarter_number:
        return None

    current_value = _current_metric_value(parsed.metric, ctx)
    if current_value is None:
        return None

    expr = parsed.target_expr.strip()
    if not expr:
        return None
    if "翻倍" in expr:
        return current_value >= 60
    match = re.search(r">=\s*(\d+)", expr)
    if match:
        return current_value >= int(match.group(1))
    if "+50%" in expr:
        return current_value >= 50
    if "增长" in expr:
        return current_value >= 50
    return None


def _current_metric_value(metric: str, ctx: SettlementContext) -> int | None:
    stats: Stats = ctx.stats_after_immediate
    return {
        "CASH": stats.CASH,
        "MORALE": stats.MORALE,
        "BOARD": stats.BOARD,
        "FACE": stats.FACE,
    }.get(metric)


def _employee_event_type(
    mood: str,
) -> Literal[
    "decision_seen", "promise_made", "promise_broken", "layoff", "press_quote", "betrayal", "favor"
]:
    if mood in {"anxious", "angry", "tired", "numb"}:
        return "betrayal"
    return "favor"


def _fit_quarter_report(*parts: str) -> str:
    text = "；".join(part.strip() for part in parts if part.strip())
    if not text:
        text = "本季结算信息不足。"
    if len(text) < 80:
        text = f"{text}。"
    while len(text) < 80:
        text = f"{text}继续发酵，组织与市场都在等一个更清晰的回应。"
    return clamp_text(text, 150)
