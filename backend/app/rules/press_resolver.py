"""Press evaluation rule resolver."""

from __future__ import annotations

from typing import Literal, cast

from pydantic import BaseModel, ConfigDict

from app.domain import MediaHeadline, PressBundle, PressEvaluation, PressInput, StatsDelta
from app.llm.schema import PressEvalRaw
from app.services.settlement_aggregator import SettlementContext

from ._utils import (
    MEDIA_OUTLET_POOL,
    clamp_int,
    clamp_text,
    normalize_choice,
    normalize_outlet,
    normalize_tone,
    stats_delta_from_mapping,
)


class PressResolveResult(BaseModel):
    """Final authority result produced from press raw output."""

    model_config = ConfigDict(frozen=True, strict=True)

    press_bundle: PressBundle
    extra_metrics_delta: StatsDelta


PressResolution = PressResolveResult


class PressResolver:
    """Turn validated press raw output into authoritative press output."""

    def resolve(self, ctx: SettlementContext, raw: PressEvalRaw) -> PressResolveResult:
        press_input = _require_press_input(ctx)
        raw_metrics_delta = stats_delta_from_mapping(
            {key: clamp_int(value, -25, 15) for key, value in raw.metricsDelta.items()}
        )
        evaluation = PressEvaluation(
            scores=dict(raw.scores),
            memorable_quote=clamp_text(raw.memorableQuote, 80),
            biggest_flaw=clamp_text(raw.biggestFlaw, 120),
            media_angle=cast(
                Literal["金句传播", "漏洞放大", "模糊带过"],
                normalize_choice(
                    raw.mediaAngle,
                    ("金句传播", "漏洞放大", "模糊带过"),
                    fallback="模糊带过",
                    kind="media_angle",
                ),
            ),
            stat_impact=raw_metrics_delta,
        )
        headlines = _build_headlines(ctx, raw)
        press_bundle = PressBundle(
            input=press_input.model_copy(deep=True),
            evaluation=evaluation,
            headlines=headlines,
        )
        return PressResolveResult(
            press_bundle=press_bundle,
            extra_metrics_delta=raw_metrics_delta,
        )


def _build_headlines(ctx: SettlementContext, raw: PressEvalRaw) -> list[MediaHeadline]:
    stats = ctx.stats_after_immediate
    outlets = _pick_outlets(stats)
    headlines: list[MediaHeadline] = []
    for outlet in outlets[:3]:
        tone = _tone_for_outlet(outlet)
        headline_text = _headline_for_outlet(outlet, raw, stats)
        summary_source = (
            raw.memorableQuote
            if "金句" in headline_text or raw.mediaAngle == "金句传播"
            else raw.biggestFlaw
        )
        headlines.append(
            MediaHeadline(
                outlet=cast(
                    Literal["36 氪", "彭博体", "晚点 LatePost", "虎嗅", "钛媒体", "脉脉自媒体"],
                    normalize_outlet(outlet),
                ),
                headline=clamp_text(headline_text, 22),
                tone=cast(
                    Literal["positive", "neutral", "negative", "mocking"],
                    normalize_tone(tone),
                ),
                summary=clamp_text(summary_source, 150),
            )
        )
    return headlines


def _pick_outlets(stats: object) -> list[str]:
    cash = getattr(stats, "CASH", 0)
    morale = getattr(stats, "MORALE", 0)
    face = getattr(stats, "FACE", 0)
    board = getattr(stats, "BOARD", 0)

    outlets: list[str] = []
    if cash < 30:
        outlets.extend(["36 氪", "彭博体"])
    if face < 40:
        outlets.extend(["虎嗅", "晚点 LatePost"])
    if morale < 30:
        outlets.append("脉脉自媒体")
    if board < 40:
        outlets.append("钛媒体")
    if not outlets:
        outlets.append(MEDIA_OUTLET_POOL[0])

    deduped: list[str] = []
    for outlet in outlets:
        if outlet not in deduped:
            deduped.append(outlet)
    return deduped


def _headline_for_outlet(outlet: str, raw: PressEvalRaw, stats: object) -> str:
    cash = getattr(stats, "CASH", 0)
    morale = getattr(stats, "MORALE", 0)
    face = getattr(stats, "FACE", 0)

    if cash < 30:
        return f"金句{raw.memorableQuote}"
    if face < 40:
        return f"漏洞{raw.biggestFlaw}"
    if morale < 30:
        return f"热议{raw.biggestFlaw or raw.memorableQuote}"
    if outlet == "脉脉自媒体":
        return f"热议{raw.biggestFlaw}"
    if raw.mediaAngle == "金句传播":
        return raw.memorableQuote
    return raw.biggestFlaw


def _tone_for_outlet(outlet: str) -> str:
    if outlet == "脉脉自媒体":
        return "mocking"
    if outlet in {"虎嗅", "晚点 LatePost"}:
        return "negative"
    return "neutral"


def _require_press_input(ctx: SettlementContext) -> PressInput:
    if ctx.press_input is None:
        raise ValueError("press_input is required for press resolution")
    return ctx.press_input
