"""Test factories."""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

from app.domain import (
    BoardReaction,
    BoomerangSeed,
    Company,
    DeathCause,
    DecisionCard,
    DecisionCategory,
    Employee,
    EmployeeGossip,
    Faction,
    GossipLead,
    GossipReliability,
    LegacyType,
    LegacyUnlock,
    MemoryActor,
    MemoryEntry,
    MetaProgress,
    Mood,
    PersonalityTag,
    PressEvaluation,
    PressInput,
    PressType,
    Promise,
    PromiseSource,
    PromiseTarget,
    Quarter,
    QuarterPhase,
    RivalAction,
    ScheduledEvent,
    Settlement,
    Stats,
    StatsDelta,
)

__all__ = (
    "build_company",
    "build_decision_card",
    "build_agent_memory",
    "build_employee",
    "build_gossip_lead",
    "build_legacy_unlock",
    "build_meta_progress",
    "build_promise",
    "build_press_evaluation",
    "build_press_input",
    "build_quarter",
    "build_scheduled_event",
    "build_settlement",
    "build_stats",
)


def build_stats(**overrides: object) -> Stats:
    values: dict[str, object] = {
        "CASH": 45,
        "MORALE": 50,
        "BOARD": 50,
        "FACE": 60,
    }
    values.update(overrides)
    return Stats(**values)


def build_company(**overrides: object) -> Company:
    values: dict[str, object] = {
        "name": "星火集团",
        "business": "卖月亮咖啡",
        "absurdity": 3,
        "founding_motto": "先活下去再说",
        "death_causes": [
            DeathCause(category="financial", description="现金流断裂后直接停摆"),
            DeathCause(category="trust", description="员工和董事会同时失去信任"),
        ],
        "starting_promises": [],
        "founded_year": 2024,
    }
    values.update(overrides)
    return Company.from_template(values)


def build_decision_card(**overrides: object) -> DecisionCard:
    values: dict[str, object] = {
        "id": "D_LAYOFF_01",
        "category": DecisionCategory.LAYOFF,
        "title": "裁员止血",
        "description": "先砍人头再谈效率",
        "immediate_effect": StatsDelta(CASH=8, MORALE=-10, BOARD=2, FACE=-4),
        "flavor": "账面好看，气氛难看",
        "long_term_hint": "三季后会反噬",
        "boomerang_seeds": [
            BoomerangSeed(
                delay_quarters=2,
                probability=0.6,
                description="核心员工开始流失",
                effect=StatsDelta(MORALE=-5, FACE=-3),
            ),
        ],
    }
    values.update(overrides)
    return DecisionCard(**values)


def build_employee(**overrides: object) -> Employee:
    values: dict[str, object] = {
        "id": f"E-{uuid4().hex[:8]}",
        "name": "张三",
        "role": "后端工程师",
        "competence": 65,
        "loyalty": 55,
        "stress": 40,
        "personality_tag": PersonalityTag.GOOD_PERSON,
        "faction": Faction.NEUTRAL,
        "relationships": [],
        "hidden_secrets": [],
        "attitude_to_player": 50,
        "current_goal": None,
        "mood": Mood.NEUTRAL,
    }
    values.update(overrides)
    return Employee(**values)


def build_press_input(**overrides: object) -> PressInput:
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
        "submitted_at": datetime(2026, 5, 23, 9, 0, tzinfo=UTC),
    }
    values.update(overrides)
    return PressInput(**values)


def build_press_evaluation(**overrides: object) -> PressEvaluation:
    values: dict[str, object] = {
        "scores": {
            "contentCompleteness": 72,
            "issueResponse": 64,
            "overpromise": 18,
            "logicClarity": 61,
            "confidence": 55,
            "riskAvoidance": 49,
            "memorableQuote": 77,
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


def build_settlement(**overrides: object) -> Settlement:
    values: dict[str, object] = {
        "quarter": 3,
        "quarter_report": (
            "本季像一场按财务口径包装的急诊：现金流被说成纪律，裁员被说成优化，董事会被说成耐心，"
            "市场却只看见我们一边止血一边自我感动。匿名员工评价：还活着，但像在等下一次坏消息。"
        ),
        "board_reaction": BoardReaction(
            speech="先把表格补齐，再谈下一步。",
            patience_delta=-1,
            vote="abstain",
        ),
        "employee_gossip": EmployeeGossip(
            speaker="老周",
            line="大家都在等下一条坏消息。",
            mood="tired",
        ),
        "rival_action": RivalAction(
            rival_name="竞品A",
            action="price_war",
            description="对手趁乱宣布全线降价",
            expected_damage=StatsDelta(CASH=-6, FACE=-4),
        ),
        "market_signal": "bear",
        "metrics_delta": StatsDelta(CASH=-4, MORALE=-3, BOARD=-1, FACE=-5),
        "scheduled_events_added": ["boom_layoff_01"],
    }
    values.update(overrides)
    return Settlement(**values)


def build_quarter(**overrides: object) -> Quarter:
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
    values.update(overrides)
    return Quarter(**values)


def build_gossip_lead(**overrides: object) -> GossipLead:
    values: dict[str, object] = {
        "id": f"G-{uuid4().hex[:8]}",
        "quarter": 1,
        "scene": "tearoom",
        "speaker_id": None,
        "text": "茶水间里有人说项目方向快变了",
        "reliability": GossipReliability.RUMOR,
        "is_truth": False,
        "linked_employee_ids": [],
        "ap_cost": 1,
    }
    values.update(overrides)
    return GossipLead(**values)


def build_promise(**overrides: object) -> Promise:
    values: dict[str, object] = {
        "id": f"P-{uuid4().hex[:8]}",
        "quarter_made": 1,
        "source": PromiseSource.PRESS,
        "text": "Q3 我们会把现金流翻倍。",
        "parsed": PromiseTarget(metric="CASH", target_expr="翻倍", deadline_quarter=3),
        "fulfilled": None,
        "judged_at_quarter": None,
    }
    values.update(overrides)
    return Promise(**values)


def build_agent_memory(**overrides: object) -> MemoryEntry:
    values: dict[str, object] = {
        "id": f"M-{uuid4().hex[:8]}",
        "actor": MemoryActor.BOARD,
        "actor_id": None,
        "quarter": 1,
        "event_type": "decision_seen",
        "summary": "董事会看过了这次决策。",
        "weight": 3,
    }
    values.update(overrides)
    return MemoryEntry(**values)


def build_scheduled_event(**overrides: object) -> ScheduledEvent:
    values: dict[str, object] = {
        "id": f"S-{uuid4().hex[:8]}",
        "source_decision_id": f"D-{uuid4().hex[:8]}",
        "fire_quarter": 2,
        "description": "下季度董事会追责。",
        "effect_on_fire": StatsDelta(BOARD=-5),
        "resolved": False,
    }
    values.update(overrides)
    return ScheduledEvent(**values)


def build_legacy_unlock(**overrides: object) -> LegacyUnlock:
    values: dict[str, object] = {
        "type": LegacyType.PR_EXPERIENCE,
        "label_zh": "危机公关",
        "description": "你知道道歉怎么说。",
        "effect_summary": "下轮发布会基础分 +5",
        "earned_at_run_id": f"R-{uuid4().hex[:8]}",
        "earned_at_quarter": 4,
    }
    values.update(overrides)
    return LegacyUnlock(**values)


def build_meta_progress(**overrides: object) -> MetaProgress:
    values: dict[str, object] = {
        "player_id": str(uuid4()),
        "schema_version": 1,
        "unlocked_legacies": [],
        "unlocked_styles": [],
        "death_log": [],
        "press_archive": [],
        "total_runs": 0,
    }
    values.update(overrides)
    return MetaProgress(**values)
