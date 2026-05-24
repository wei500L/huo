"""Tests for settlement prompt building."""

from __future__ import annotations

from datetime import UTC, datetime

from app.domain import DeathReason, MemoryWindow
from app.llm import PromptBuilder, PromptBundle
from app.services.settlement_aggregator import SettlementContext
from tests.factories import (
    build_agent_memory,
    build_decision_card,
    build_press_input,
    build_promise,
    build_scheduled_event,
    build_stats,
)


def test_build_director_prompt_outputs_expected_bundle() -> None:
    ctx = _build_context()
    bundle = PromptBuilder().build_director_prompt(ctx)

    assert isinstance(bundle, PromptBundle)
    assert bundle.prompt_kind == "director"
    assert bundle.max_tokens == 1200
    assert bundle.temperature == 0.7
    assert "总导演" in bundle.system
    assert all(
        key in bundle.system
        for key in (
            "boardReaction",
            "employeeGossip",
            "mediaHeadline",
            "rivalAction",
            "marketSignal",
            "metricsDelta",
            "quarterReport",
        )
    )
    assert "SALES" not in bundle.system
    assert "MKT" not in bundle.system
    assert "当前 4 指标" in bundle.user
    assert "CASH: 52" in bundle.user
    assert "MORALE: 46" in bundle.user
    assert "BOARD: 54" in bundle.user
    assert "FACE: 56" in bundle.user
    assert "裁员止血" in bundle.user
    assert "先砍人头再谈效率" in bundle.user
    assert bundle.estimated_input_tokens > 0
    assert bundle.estimated_input_tokens < len(bundle.user)


def test_build_press_eval_prompt_outputs_expected_bundle() -> None:
    bundle = PromptBuilder().build_press_eval_prompt(_build_context())

    assert isinstance(bundle, PromptBundle)
    assert bundle.prompt_kind == "press_eval"
    assert bundle.max_tokens == 800
    assert bundle.temperature == 0.6
    assert "```" in bundle.user
    assert bundle.user.count("    ```") == 2
    assert all(
        key in bundle.system
        for key in (
            "contentCompleteness",
            "issueResponse",
            "overpromise",
            "logicClarity",
            "confidence",
            "riskAvoidance",
            "quotability",
            "weaknessExposed",
            "authenticity",
        )
    )
    assert "metricsDelta" in bundle.system


def test_build_death_report_prompt_outputs_expected_bundle() -> None:
    bundle = PromptBuilder().build_death_report_prompt(
        _build_context(),
        death_reason=DeathReason.BANKRUPTCY,
    )

    assert isinstance(bundle, PromptBundle)
    assert bundle.prompt_kind == "death_report"
    assert bundle.max_tokens == 1200
    assert bundle.temperature == 0.8
    assert "破产清算" in bundle.user
    assert "history_summary" in bundle.user
    assert "agent_memory" in bundle.user
    assert "4 指标走势" in bundle.user
    assert "所有承诺及兑现情况" in bundle.user
    assert "obituary" in bundle.system
    assert "300-500" in bundle.system
    assert "biggestMistakeDecisionId" in bundle.system
    assert "lastEmployee" in bundle.system
    assert "headlines" in bundle.system
    assert "legacyUnlocks" in bundle.system


def test_estimated_input_tokens_are_reasonable() -> None:
    bundle = PromptBuilder().build_director_prompt(_build_context())
    assert bundle.estimated_input_tokens > 0
    assert bundle.estimated_input_tokens < len(bundle.user)


def _build_context(
    *,
    transcript: str | None = None,
    history_summary: list[str] | None = None,
) -> SettlementContext:
    decision = build_decision_card(
        title="裁员止血",
        description="先砍人头再谈效率",
        flavor="账面好看，气氛难看",
    )
    transcript_text = transcript or (
        "我们会持续回应市场关切，并确保现金流、产品和组织调整同步推进，"
        "避免短期波动影响长期执行。"
    )
    press_input = build_press_input(
        transcript=transcript_text,
        submitted_at=datetime(2026, 5, 23, 9, 0, tzinfo=UTC),
    )
    return SettlementContext(
        session_id="S-001",
        player_id="P-001",
        quarter_number=3,
        company_brief={"name": "星火集团", "business": "卖月亮咖啡"},
        stats_before_immediate=build_stats(CASH=45, MORALE=50, BOARD=50, FACE=60),
        stats_after_immediate=build_stats(CASH=52, MORALE=46, BOARD=54, FACE=56),
        selected_decision=decision,
        immediate_effect_applied=decision.immediate_effect,
        gossip_collected=[],
        press_input=press_input,
        press_type=press_input.press_type,
        press_must_answer=list(press_input.must_answer_topics),
        active_promises=[build_promise()],
        agent_memory_window=MemoryWindow(
            entries=[
                build_agent_memory(id="M-01", quarter=3, summary="董事会盯着现金流。"),
                build_agent_memory(id="M-02", quarter=3, summary="员工在茶水间讨论裁员。"),
            ]
        ),
        scheduled_events_firing_this_quarter=[build_scheduled_event()],
        history_summary=history_summary or ["Q1 勉强撑住，Q2 开始失血。"],
        employees_snapshot=[],
        meta_buff_signature="PR_EXPERIENCE",
        rng_seed_for_aggregation=42,
        aggregated_at=datetime(2026, 5, 23, 10, 0, tzinfo=UTC),
    )
