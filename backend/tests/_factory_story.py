"""Story and runtime-facing test factories."""

from __future__ import annotations

from datetime import UTC, datetime
from random import Random

from app.domain import (
    MemoryActor,
    MemoryEntry,
    MetaProgress,
    PressEvaluation,
    PressInput,
    PressType,
    Quarter,
    QuarterPhase,
    Settlement,
    StatsDelta,
)

from ._factory_domain import (
    _prefixed_hex,
    _seed_uuid,
)

__all__ = (
    "build_agent_memory",
    "build_gossip_lead",
    "build_legacy_unlock",
    "build_meta_progress",
    "build_press_evaluation",
    "build_press_input",
    "build_promise",
    "build_quarter",
    "build_scheduled_event",
    "build_settlement",
)

_FIXED_NOW = datetime(2026, 5, 23, 9, 0, tzinfo=UTC)


def build_press_input(seed: int | None = None, **overrides: object) -> PressInput:
    rng = Random(seed)
    values: dict[str, object] = {
        "quarter": 3,
        "press_type": PressType.CRISIS,
        "must_answer_topics": ["现金流", "裁员"],
        "transcript": (
            "我们会持续回应市场关切，并确保现金流、产品和组织调整同步推进，"
            "避免短期波动影响长期执行。"
        ),
        "duration_s": 92.5,
        "word_count": 128,
        "flags": ["brand_replaced"],
        "submitted_at": _FIXED_NOW.replace(minute=(rng.randrange(60) if seed is not None else 0)),
    }
    values.update(overrides)
    return PressInput(**values)


def build_press_evaluation(seed: int | None = None, **overrides: object) -> PressEvaluation:
    rng = Random(seed)
    values: dict[str, object] = {
        "scores": {
            "contentCompleteness": 72 + (rng.randrange(3) if seed is not None else 0),
            "issueResponse": 64,
            "overpromise": 18,
            "logicClarity": 61,
            "confidence": 55,
            "riskAvoidance": 49,
            "quotability": 77,
            "weaknessExposed": 58,
            "authenticity": 63,
        },
        "memorable_quote": "我们不是没有答案，只是答案还在路上。",
        "biggest_flaw": "回避了具体时间表",
        "media_angle": "漏洞放大",
        "stat_impact": StatsDelta(CASH=-2, MORALE=-3, BOARD=1, FACE=-1),
    }
    values.update(overrides)
    return PressEvaluation(**values)


def build_settlement(seed: int | None = None, **overrides: object) -> Settlement:
    rng = Random(seed)
    values: dict[str, object] = {
        "quarter": 3,
        "quarter_report": (
            "本季像一场按财务口径包装的急诊：现金流被说成纪律，裁员被说成优化，董事会被说成耐心，"
            "市场却只看见我们一边止血一边自我感动。匿名员工评价：还活着，但像在等下一次坏消息。"
        ),
        "board_reaction": {
            "speech": "先把表格补齐，再谈下一步。",
            "patience_delta": -1 if seed is None else -1 + (rng.randrange(2) - 1),
            "vote": "abstain",
        },
        "employee_gossip": {
            "speaker": "老周",
            "line": "大家都在等下一条坏消息。",
            "mood": "tired",
        },
        "rival_action": {
            "rival_name": "竞品A",
            "action": "price_war",
            "description": "对手趁乱宣布全线降价",
            "expected_damage": {"CASH": -6, "MORALE": 0, "BOARD": 0, "FACE": -4},
        },
        "market_signal": "bear",
        "metrics_delta": {"CASH": -4, "MORALE": -3, "BOARD": -1, "FACE": -5},
        "scheduled_events_added": ["boom_layoff_01"],
    }
    values.update(overrides)
    return Settlement.model_validate(values)


def build_quarter(seed: int | None = None, **overrides: object) -> Quarter:
    rng = Random(seed)
    market_moods = ["bull", "neutral", "bear", "crisis"]
    values: dict[str, object] = {
        "number": 1,
        "phase": QuarterPhase.BRIEFING,
        "briefing": None,
        "decision_cards": [],
        "selected_decision_id": None,
        "gossip_collected": [],
        "collected_leads": [],
        "press_input": None,
        "press_bundle": None,
        "settlement": None,
        "ap_remaining": 10,
    }
    if seed is not None:
        values["briefing"] = {
            "quarter": 1,
            "market_mood": market_moods[rng.randrange(len(market_moods))],
            "headline_hint": "先稳住组织和现金",
            "hidden_risks": ["董事会翻脸"],
        }
    values.update(overrides)
    return Quarter(**values)


def build_gossip_lead(seed: int | None = None, **overrides: object):
    from app.domain import GossipLead, GossipReliability

    rng = Random(seed)
    values: dict[str, object] = {
        "id": _seed_uuid(seed, prefix="gossip"),
        "quarter": 1,
        "scene": "tearoom"
        if seed is None
        else rng.choice(
            ["tearoom", "elevator", "meeting_room", "workstation", "rooftop", "smoking_area"]
        ),
        "speaker_id": None,
        "text": "茶水间里有人说项目方向快变了",
        "reliability": GossipReliability.RUMOR,
        "is_truth": False,
        "linked_employee_ids": [],
        "ap_cost": 1,
    }
    values.update(overrides)
    return GossipLead(**values)


def build_promise(seed: int | None = None, **overrides: object):
    from app.domain import Promise, PromiseSource, PromiseTarget

    values: dict[str, object] = {
        "id": _seed_uuid(seed, prefix="promise"),
        "quarter_made": 1,
        "source": PromiseSource.PRESS,
        "text": "Q3 我们会把现金流翻倍。",
        "parsed": PromiseTarget(metric="CASH", target_expr="翻倍", deadline_quarter=3),
        "fulfilled": None,
        "judged_at_quarter": None,
    }
    values.update(overrides)
    return Promise(**values)


def build_agent_memory(seed: int | None = None, **overrides: object) -> MemoryEntry:

    values: dict[str, object] = {
        "id": _seed_uuid(seed, prefix="memory"),
        "actor": MemoryActor.BOARD,
        "actor_id": None,
        "quarter": 1,
        "event_type": "decision_seen",
        "summary": "董事会看过了这次决策。",
        "weight": 3,
    }
    values.update(overrides)
    return MemoryEntry(**values)


def build_scheduled_event(seed: int | None = None, **overrides: object):
    from app.domain import ScheduledEvent

    values: dict[str, object] = {
        "id": _seed_uuid(seed, prefix="scheduled"),
        "source_decision_id": _seed_uuid(seed, prefix="decision"),
        "fire_quarter": 2,
        "description": "下季度董事会追责。",
        "effect_on_fire": StatsDelta(BOARD=-5),
        "resolved": False,
    }
    values.update(overrides)
    return ScheduledEvent(**values)


def build_legacy_unlock(seed: int | None = None, **overrides: object):
    from app.domain import LegacyType, LegacyUnlock

    values: dict[str, object] = {
        "type": LegacyType.PR_EXPERIENCE,
        "label_zh": "危机公关",
        "description": "你知道道歉怎么说。",
        "effect_summary": "下轮发布会基础分 +5",
        "earned_at_run_id": _prefixed_hex("R", seed),
        "earned_at_quarter": 4,
    }
    values.update(overrides)
    return LegacyUnlock(**values)


def build_meta_progress(seed: int | None = None, **overrides: object) -> MetaProgress:
    values: dict[str, object] = {
        "player_id": _seed_uuid(seed, prefix="player"),
        "schema_version": 1,
        "unlocked_legacies": [],
        "unlocked_styles": [],
        "death_log": [],
        "press_archive": [],
        "total_runs": 0,
    }
    values.update(overrides)
    return MetaProgress(**values)
