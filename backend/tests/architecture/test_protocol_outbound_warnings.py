"""Architecture guardrail for outbound protocol serialization."""

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
from app.protocol import DeathReportBundle, GameSnapshot, GossipResult, SettlementBundle
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


def test_outbound_serialization_never_exposes_warn_fields() -> None:
    company = build_company()
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
        briefing=Briefing(
            quarter=2,
            market_mood="crisis",
            headline_hint="现金流告急",
            hidden_risks=["董事会翻脸", "媒体追问"],
        ),
        decision_cards=[build_decision_card()],
        selected_decision_id="D_LAYOFF_01",
        gossip_collected=["茶水间风声"],
        press_input=press_input,
        press_bundle=press_bundle,
        settlement=build_settlement(),
        ap_remaining=6,
    )
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

    game_snapshot = GameSnapshot.from_domain(
        session_id="S-0001",
        player_id="P-0001",
        company=company,
        stats=build_stats(),
        quarter=quarter,
        history=[
            HistoryEntry(
                quarter=1,
                decision_id="D_LAYOFF_01",
                press_bundle_id=None,
                stats_before=Stats(CASH=50, MORALE=50, BOARD=50, FACE=60),
                stats_after=Stats(CASH=46, MORALE=47, BOARD=49, FACE=55),
                settlement_summary="现金流暂时止血，但舆论继续发酵。",
            )
        ],
        meta_progress=meta_progress,
    )
    gossip_result = GossipResult.from_domain(
        session_id="S-0001",
        quarter_number=2,
        lead=build_gossip_lead(is_truth=True),
        ap_remaining=5,
    )
    settlement_bundle = SettlementBundle.from_domain(
        session_id="S-0001",
        quarter_number=3,
        settlement=build_settlement(),
        press_bundle=None,
        new_stats=build_stats(CASH=0, MORALE=43, BOARD=48, FACE=49),
        history_added=HistoryEntry(
            quarter=3,
            decision_id="D_LAYOFF_01",
            press_bundle_id="PB-0001",
            stats_before=Stats(CASH=40, MORALE=46, BOARD=49, FACE=54),
            stats_after=Stats(CASH=36, MORALE=43, BOARD=48, FACE=49),
            settlement_summary="本季继续承压，但没有立刻崩盘。",
        ),
        death=DeathReason.DISGRACE,
    )
    death_report = DeathReportBundle.from_domain(
        session_id="S-0001",
        death_log_entry=DeathLogEntry(
            run_id="R-0001",
            company_name=company.name,
            business=company.business,
            died_at_quarter=4,
            death_reason=DeathReason.DISGRACE,
            obituary="公司结束了这轮运行。",
            biggest_mistake_decision_id="D_LAYOFF_01",
            last_employee_quote="我们已经尽力了。",
            headlines=["公司结束", "下一轮再来"],
        ),
        legacy_unlocks=[build_legacy_unlock()],
        styles_unlocked=[ManagementStyle.FACE_KEEPER],
        last_employee_name="老周",
        last_employee_quote="我们已经尽力了。",
    )

    payloads = [
        game_snapshot.model_dump(mode="json", by_alias=True),
        gossip_result.model_dump(mode="json", by_alias=True),
        settlement_bundle.model_dump(mode="json", by_alias=True),
        death_report.model_dump(mode="json", by_alias=True),
    ]
    forbidden = {
        "hidden_secrets",
        "hiddenSecrets",
        "is_truth",
        "isTruth",
        "hidden_risks",
        "hiddenRisks",
        "internal_eval",
        "internalEval",
    }

    seen_keys: set[str] = set()
    for payload in payloads:
        seen_keys.update(_collect_keys(payload))

    assert forbidden.isdisjoint(seen_keys)


def _collect_keys(value: object) -> set[str]:
    keys: set[str] = set()
    if isinstance(value, dict):
        for key, nested in value.items():
            keys.add(key)
            keys.update(_collect_keys(nested))
        return keys
    if isinstance(value, list):
        for item in value:
            keys.update(_collect_keys(item))
    return keys
