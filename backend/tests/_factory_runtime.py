"""Runtime and raw payload test factories."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from random import Random
from uuid import UUID

from app.domain import MemoryWindow, Stats
from app.llm._parser_defaults import (
    canonical_death_base,
    canonical_director_base,
    canonical_press_base,
)
from app.repo.protocols import GameSession
from app.services.settlement_aggregator import SettlementContext

from ._factory_domain import (
    build_company,
    build_decision_card,
    build_employees,
    build_stats,
)
from ._factory_story import (
    build_agent_memory,
    build_gossip_lead,
    build_meta_progress,
    build_press_input,
    build_promise,
    build_quarter,
    build_scheduled_event,
)

__all__ = (
    "build_death_report_raw",
    "build_director_raw",
    "build_press_eval_raw",
    "build_session",
    "build_settlement_context",
)

_FIXED_NOW = datetime(2026, 5, 23, 9, 0, tzinfo=UTC)


def build_session(seed: int | None = None, **overrides: object) -> GameSession:
    rng = Random(seed)
    company_seed = rng.randrange(2**32) if seed is not None else None
    employee_seed = rng.randrange(2**32) if seed is not None else None
    stats_seed = rng.randrange(2**32) if seed is not None else None
    quarter_seed = rng.randrange(2**32) if seed is not None else None

    company = build_company(seed=company_seed)
    employees = build_employees(12, seed=employee_seed)
    stats = Stats.starting(seed=stats_seed) if seed is not None else build_stats()
    briefing = {
        "quarter": 1,
        "market_mood": ["bull", "neutral", "bear", "crisis"][
            (Random(quarter_seed).randrange(4) if quarter_seed is not None else 1)
        ],
        "headline_hint": f"{company.business} 先稳住现金再说",
        "hidden_risks": [cause.description for cause in company.death_causes[:2]],
    }
    quarter = build_quarter(
        seed=quarter_seed,
        briefing=briefing,
    )
    now = _FIXED_NOW + timedelta(minutes=(seed or 0) % 60)
    session = GameSession(
        id=_seed_uuid("session", seed),
        player_id=_seed_uuid("player", seed),
        company=company,
        stats=stats,
        quarter=quarter,
        employees=employees,
        history=[],
        promise_log=[],
        agent_memory=MemoryWindow(entries=[]),
        scheduled_events=[],
        status="active",
        created_at=now,
        updated_at=now,
    )
    return session.model_copy(update=overrides) if overrides else session


def build_settlement_context(seed: int | None = None, **overrides: object) -> SettlementContext:
    session = build_session(seed=seed)
    decision = build_decision_card(seed=seed)
    press_input = build_press_input(seed=seed, quarter=3)
    stats_before = session.stats
    stats_after = stats_before.apply_delta(decision.immediate_effect)
    meta = build_meta_progress(seed=seed)
    context = SettlementContext(
        session_id=session.id,
        player_id=session.player_id,
        quarter_number=3,
        company_brief={
            "name": session.company.name,
            "business": session.company.business,
            "founding_motto": session.company.founding_motto,
            "deathCausesSummary": [cause.description for cause in session.company.death_causes],
            "hiddenRisks": [cause.description for cause in session.company.death_causes[:2]],
        },
        stats_before_immediate=stats_before,
        stats_after_immediate=stats_after,
        selected_decision=decision,
        immediate_effect_applied=decision.immediate_effect,
        gossip_collected=[build_gossip_lead(seed=seed, quarter=3)],
        press_input=press_input,
        press_type=press_input.press_type,
        press_must_answer=["坏消息来源", "止血计划", "外界质疑"],
        active_promises=[build_promise(seed=seed, quarter_made=1)],
        agent_memory_window=MemoryWindow(entries=[build_agent_memory(seed=seed)]),
        scheduled_events_firing_this_quarter=[build_scheduled_event(seed=seed, fire_quarter=3)],
        history_summary=["Q1 稳住了。", "Q2 开始失血。"],
        employees_snapshot=[
            employee.model_copy(update={"hidden_secrets": []}) for employee in session.employees
        ],
        meta_buff_signature="/".join(
            unlock.effect_summary for unlock in meta.unlocked_legacies if unlock.effect_summary
        ),
        rng_seed_for_aggregation=(seed or 0) * 97 + 13,
        aggregated_at=_FIXED_NOW,
    )
    return context.model_copy(update=overrides) if overrides else context


def build_director_raw(seed: int | None = None, **overrides: object) -> dict[str, object]:
    rng = Random(seed)
    base = canonical_director_base()
    base["boardReaction"]["speech"] = (
        [
            "先看结果，再看解释。",
            "表格先补齐，动作后补。",
            "先让现金流喘气，再谈理想。",
        ][rng.randrange(3)]
        if seed is not None
        else base["boardReaction"]["speech"]
    )
    base["employeeGossip"]["speaker"] = (
        ["小周", "老周", "陈砚"][rng.randrange(3)]
        if seed is not None
        else base["employeeGossip"]["speaker"]
    )
    base["mediaHeadline"]["headline"] = (
        [
            "公司先止血再求活路",
            "组织调整成了唯一话题",
            "现金流压力继续外溢",
        ][rng.randrange(3)]
        if seed is not None
        else base["mediaHeadline"]["headline"]
    )
    base["rivalAction"]["move"] = (
        [
            "先观察空档，准备趁乱抢客户。",
            "悄悄调价，逼迫对方失速。",
            "等对手自己犯错再下场。",
        ][rng.randrange(3)]
        if seed is not None
        else base["rivalAction"]["move"]
    )
    if seed is not None:
        base["metricsDelta"] = {"CASH": 1, "MORALE": 0, "BOARD": 1, "FACE": 1}
        base["rivalAction"]["expectedDamage"] = {"CASH": -1, "MORALE": 0, "BOARD": 0, "FACE": -1}
    base["quarterReport"] = (
        "董事会暂时收住火气，但并没有真正放松警惕；员工在茶水间里反复咀嚼组织调整的信号，"
        "媒体盯住现金流和执行节奏，对手保持克制，市场则把这家公司视为一场还没结束的止血实验。"
    )
    return _merge_dict(base, overrides)


def build_press_eval_raw(seed: int | None = None, **overrides: object) -> dict[str, object]:
    rng = Random(seed)
    base = canonical_press_base()
    base["scores"] = {
        key: min(100, max(0, value + (rng.randrange(4) - 1 if seed is not None else 0)))
        for key, value in base["scores"].items()
    }
    base["memorableQuote"] = (
        [
            "我们不回避问题，但也不会靠口号续命。",
            "我们把问题摊开说，而不是绕着走。",
            "今天讲清楚，明天才有得做。",
        ][rng.randrange(3)]
        if seed is not None
        else base["memorableQuote"]
    )
    if seed is not None:
        base["metricsDelta"] = {"CASH": 0, "MORALE": 1, "BOARD": 0, "FACE": 2}
    return _merge_dict(base, overrides)


def build_death_report_raw(seed: int | None = None, **overrides: object) -> dict[str, object]:
    rng = Random(seed)
    base = canonical_death_base()
    if seed is not None:
        base["obituary"] = base["obituary"] + " 复盘内容按 seed 轻微扰动，以保持确定性。"
        base["lastEmployee"] = {"name": "小周", "quote": "茶水间里只剩下沉默。"}
        base["legacyUnlocks"] = ["PR_EXPERIENCE"] if rng.randrange(2) == 0 else []
    return _merge_dict(base, overrides)


def _merge_dict(base: dict[str, object], overrides: dict[str, object]) -> dict[str, object]:
    merged = dict(base)
    for key, value in overrides.items():
        existing = merged.get(key)
        if isinstance(existing, dict) and isinstance(value, dict):
            merged[key] = _merge_dict(existing, value)
        else:
            merged[key] = value
    return merged


def _seed_uuid(prefix: str, seed: int | None) -> str:
    if seed is None:
        return str(UUID(int=Random().getrandbits(128), version=4))
    rng = Random(f"{prefix}:{seed}")
    return str(UUID(int=rng.getrandbits(128), version=4))
