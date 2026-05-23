"""Tests for outbound protocol DTOs."""

from __future__ import annotations

from app.domain import (
    Briefing,
    DeathLogEntry,
    DeathReason,
    HistoryEntry,
    ManagementStyle,
    MediaHeadline,
    PressBundle,
    QuarterPhase,
    Stats,
)
from app.protocol import GameSnapshot, GossipResult, SettlementBundle
from tests.factories import (
    build_company,
    build_decision_card,
    build_gossip_lead,
    build_legacy_unlock,
    build_meta_progress,
    build_press_evaluation,
    build_press_input,
    build_quarter,
    build_settlement,
    build_stats,
)


def test_game_snapshot_serializes_camel_case_and_filters_warn_fields() -> None:
    company = build_company()
    stats = build_stats()
    briefing = Briefing(
        quarter=2,
        market_mood="crisis",
        headline_hint="现金流告急",
        hidden_risks=["董事会翻脸", "媒体追问"],
    )
    press_input = build_press_input()
    press_bundle = PressBundle(
        input=press_input,
        evaluation=build_press_evaluation(),
        headlines=[
            MediaHeadline(outlet="晚点 LatePost", headline="公司回应危机", tone="neutral"),
        ],
    )
    quarter = build_quarter(
        number=2,
        phase=QuarterPhase.PRESS,
        briefing=briefing,
        decision_cards=[build_decision_card()],
        selected_decision_id="D_LAYOFF_01",
        gossip_collected=["茶水间风声", "电梯间传闻"],
        press_input=press_input,
        press_bundle=press_bundle,
        settlement=build_settlement(),
        ap_remaining=7,
    )
    history = [
        HistoryEntry(
            quarter=1,
            decision_id="D_LAYOFF_01",
            press_bundle_id=None,
            stats_before=Stats(CASH=50, MORALE=50, BOARD=50, FACE=60),
            stats_after=Stats(CASH=46, MORALE=47, BOARD=49, FACE=55),
            settlement_summary="现金流暂时止血，但舆论继续发酵。",
        )
    ]
    meta_progress = build_meta_progress(
        unlocked_legacies=[build_legacy_unlock()],
        unlocked_styles=[ManagementStyle.FACE_KEEPER],
        death_log=[
            DeathLogEntry(
                run_id="R-0001",
                company_name=company.name,
                business=company.business,
                died_at_quarter=4,
                death_reason=None,
                obituary="本轮撑到了最后。",
                biggest_mistake_decision_id=None,
                last_employee_quote=None,
                headlines=["最后一轮"],
            )
        ],
        press_archive=["press-001"],
        total_runs=4,
    )

    snapshot = GameSnapshot.from_domain(
        session_id="S-0001",
        player_id="P-0001",
        company=company,
        stats=stats,
        quarter=quarter,
        history=history,
        meta_progress=meta_progress,
    )
    payload = snapshot.model_dump(mode="json", by_alias=True)

    assert payload["company"]["foundingMotto"] == company.founding_motto
    assert payload["quarter"]["apRemaining"] == 7
    assert payload["quarter"]["briefing"]["headlineHint"] == "现金流告急"
    assert "hiddenRisks" not in payload["quarter"]["briefing"]
    assert payload["quarter"]["decisionCards"][0]["immediateEffect"]["cash"] == 8
    assert payload["metaSummary"]["schemaVersion"] == 1
    assert payload["metaSummary"]["unlockedLegacies"][0]["earnedAtRunId"].startswith("R-")


def test_gossip_result_filters_truth_flag_and_uses_aliases() -> None:
    gossip = GossipResult.from_domain(
        session_id="S-0001",
        quarter_number=2,
        lead=build_gossip_lead(is_truth=True),
        ap_remaining=6,
    )
    payload = gossip.model_dump(mode="json", by_alias=True)

    assert payload["lead"]["scene"] == "tearoom"
    assert payload["lead"]["reliability"] == "RUMOR"
    assert "isTruth" not in payload["lead"]


def test_settlement_bundle_sets_death_state_explicitly() -> None:
    settlement = build_settlement()
    history_entry = HistoryEntry(
        quarter=3,
        decision_id="D_LAYOFF_01",
        press_bundle_id="PB-0001",
        stats_before=Stats(CASH=40, MORALE=46, BOARD=49, FACE=54),
        stats_after=Stats(CASH=36, MORALE=43, BOARD=48, FACE=49),
        settlement_summary="本季继续承压，但没有立刻崩盘。",
    )

    dead_bundle = SettlementBundle.from_domain(
        session_id="S-0001",
        quarter_number=3,
        settlement=settlement,
        press_bundle=None,
        new_stats=build_stats(CASH=0, MORALE=43, BOARD=48, FACE=49),
        history_added=history_entry,
        death=DeathReason.DISGRACE,
    )
    alive_bundle = SettlementBundle.from_domain(
        session_id="S-0002",
        quarter_number=2,
        settlement=settlement,
        press_bundle=None,
        new_stats=build_stats(CASH=36, MORALE=43, BOARD=48, FACE=49),
        history_added=history_entry,
        death=None,
    )

    dead_payload = dead_bundle.model_dump(mode="json", by_alias=True)

    assert dead_bundle.death is not None
    assert alive_bundle.death is None
    assert dead_payload["death"]["code"] == "DISGRACE"
