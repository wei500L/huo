"""Architecture guardrail: outbound DTOs never expose WARN fields."""

from __future__ import annotations

import json
from collections.abc import Iterable

from app.domain import (
    DeathLogEntry,
    DeathReason,
    HistoryEntry,
    ManagementStyle,
    MediaHeadline,
    PressBundle,
)
from app.protocol import (
    DeathReportBundle,
    DecisionAck,
    ErrorOutbound,
    GameSnapshot,
    GossipResult,
    PressAck,
    SettlementBundle,
    Toast,
)
from tests.factories import (
    build_company,
    build_decision_card,
    build_employee,
    build_gossip_lead,
    build_legacy_unlock,
    build_meta_progress,
    build_press_evaluation,
    build_press_input,
    build_quarter,
    build_session,
    build_settlement,
    build_stats,
)

FORBIDDEN = {
    "hidden_secrets",
    "hiddenSecrets",
    "is_truth",
    "isTruth",
    "hidden_risks",
    "hiddenRisks",
    "internal_eval",
    "internalEval",
}


def test_outbound_dtos_serialize_without_warn_fields() -> None:
    company = build_company(seed=11)
    press_input = build_press_input(seed=11)
    press_bundle = PressBundle(
        input=press_input,
        evaluation=build_press_evaluation(seed=11),
        headlines=[
            MediaHeadline(outlet="晚点 LatePost", headline="公司回应危机", tone="neutral"),
        ],
    )
    gossip = build_gossip_lead(seed=11, is_truth=True)
    settlement = build_settlement(seed=11)
    decision = build_decision_card(seed=11)
    quarter = build_quarter(
        seed=11,
        decision_cards=[decision],
        selected_decision_id=decision.id,
        gossip_collected=[gossip.id],
        collected_leads=[gossip],
        press_input=press_input,
        press_bundle=press_bundle,
        settlement=settlement,
    )
    session = build_session(
        seed=11,
        company=company,
        stats=build_stats(CASH=88, MORALE=86, BOARD=84, FACE=82),
        quarter=quarter,
        employees=[
            build_employee(seed=1, hidden_secrets=["财务备忘录"]),
            build_employee(seed=2, hidden_secrets=["竞品联络人"]),
        ],
    )
    legacy = build_legacy_unlock(seed=11)
    meta = build_meta_progress(
        seed=11,
        player_id=session.player_id,
        unlocked_legacies=[legacy],
        unlocked_styles=[ManagementStyle.FACE_KEEPER],
        death_log=[
            DeathLogEntry(
                run_id=session.id,
                company_name=company.name,
                business=company.business,
                died_at_quarter=4,
                death_reason=None,
                obituary="本轮撑到了最后。",
                headlines=["最后一轮"],
            )
        ],
        total_runs=1,
    )

    payloads = [
        GameSnapshot.from_domain(
            session_id=session.id,
            player_id=session.player_id,
            company=session.company,
            stats=session.stats,
            quarter=session.quarter,
            history=session.history,
            meta_progress=meta,
        ),
        DecisionAck.from_domain(
            session_id=session.id,
            quarter_number=quarter.number,
            card_id=decision.id,
            immediate_stats=session.stats,
            next_phase="SETTLEMENT",
        ),
        GossipResult.from_domain(
            session_id=session.id,
            quarter_number=quarter.number,
            lead=gossip,
            ap_remaining=quarter.ap_remaining,
        ),
        PressAck(
            session_id=session.id,
            quarter_number=3,
            accepted=True,
            flags=press_input.flags,
            replaced_count=1,
        ),
        SettlementBundle.from_domain(
            session_id=session.id,
            quarter_number=quarter.number,
            settlement=settlement,
            press_bundle=press_bundle,
            new_stats=session.stats,
            history_added=HistoryEntry(
                quarter=3,
                decision_id=decision.id,
                press_bundle_id=None,
                stats_before=build_stats(CASH=88, MORALE=86, BOARD=84, FACE=82),
                stats_after=session.stats,
                settlement_summary="本季继续承压，但没有立刻崩盘。",
            ),
            death=DeathReason.DISGRACE,
        ),
        DeathReportBundle.from_domain(
            session_id=session.id,
            death_log_entry=DeathLogEntry(
                run_id=session.id,
                company_name=company.name,
                business=company.business,
                died_at_quarter=4,
                death_reason=DeathReason.DISGRACE,
                obituary="公司结束了这轮运行。",
                biggest_mistake_decision_id=decision.id,
                last_employee_quote="我们已经尽力了。",
                headlines=["公司结束", "下一轮再来", "教训留下"],
            ),
            legacy_unlocks=[legacy],
            styles_unlocked=[ManagementStyle.FACE_KEEPER],
            last_employee_name="老周",
            last_employee_quote="我们已经尽力了。",
        ),
        Toast(level="info", message="ok"),
        ErrorOutbound(code="validation_error", message="invalid", retryable=False),
    ]

    failures: list[str] = []
    for index, payload in enumerate(payloads):
        dumped = payload.model_dump(mode="json", by_alias=True)
        encoded = json.dumps(dumped, ensure_ascii=False)
        for token in FORBIDDEN:
            if token in encoded:
                failures.append(f"payload[{index}] JSON contains {token}")
        failures.extend(_forbidden_paths(dumped, path=f"payload[{index}]"))

    assert not failures, "\n".join(failures)


def _forbidden_paths(value: object, path: str) -> list[str]:
    hits: list[str] = []
    if isinstance(value, dict):
        for key, nested in value.items():
            key_path = f"{path}.{key}"
            if key in FORBIDDEN:
                hits.append(key_path)
            hits.extend(_forbidden_paths(nested, key_path))
        return hits
    if isinstance(value, list):
        for index, nested in enumerate(value):
            hits.extend(_forbidden_paths(nested, f"{path}[{index}]"))
        return hits
    if isinstance(value, str):
        hits.extend(f"{path} contains {token}" for token in _contained_tokens(value))
    return hits


def _contained_tokens(value: str) -> Iterable[str]:
    return (token for token in FORBIDDEN if token in value)
