"""Four-quarter service integration loop."""

from __future__ import annotations

from uuid import uuid4

import httpx
import pytest

from app.domain import DecisionCategory, ManagementStyle, PressType, QuarterPhase, StatsDelta
from tests.factories import (
    build_decision_card,
    build_director_raw,
    build_legacy_unlock,
    build_meta_progress,
    build_press_eval_raw,
    build_stats,
)
from tests.llm_spy import SpyLLMClient, raw_json


@pytest.mark.asyncio
async def test_full_loop_4q_reaches_won_with_mock_llm_only(
    full_stack: tuple[object, ...],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    http_calls = {"count": 0}

    async def _blocked_http(*args: object, **kwargs: object) -> object:
        http_calls["count"] += 1
        raise AssertionError("real HTTP request attempted")

    monkeypatch.setattr(httpx.AsyncClient, "post", _blocked_http)
    monkeypatch.setattr(
        "app.services.decision_service.sample_decision_cards",
        _safe_decision_cards,
    )
    (
        company_service,
        decision_service,
        gossip_service,
        press_input_service,
        orchestrator,
        death_report_service,
        state_machine,
    ) = full_stack
    spy = SpyLLMClient(
        {
            "director": raw_json(build_director_raw(seed=2)),
            "press_eval": raw_json(build_press_eval_raw(seed=2)),
        }
    )
    orchestrator.llm_client = spy
    death_report_service.llm_client = spy

    player_id = str(uuid4())
    await company_service.meta_repo.save(
        build_meta_progress(
            player_id=player_id,
            unlocked_legacies=[build_legacy_unlock(seed=2)],
            unlocked_styles=[ManagementStyle.FACE_KEEPER],
        )
    )
    session = await company_service.create_new_run(player_id=player_id, rng_seed=2026)
    session = session.model_copy(
        update={"stats": build_stats(CASH=95, MORALE=95, BOARD=95, FACE=95)}
    )
    await company_service.session_repo.save(session)

    llm_calls_reported = 0
    for quarter in range(1, 5):
        await state_machine.transition_to(session.id, QuarterPhase.GOSSIP)
        await gossip_service.collect_gossip(session.id, "tearoom", rng_seed=quarter)
        await state_machine.transition_to(session.id, QuarterPhase.DECISION)
        drawn = await decision_service.draw_decision_cards(session.id, rng_seed=quarter)
        selected_id = drawn.quarter.decision_cards[0].id
        await decision_service.select_decision(session.id, selected_id, rng_seed=quarter)
        if quarter == 3:
            await press_input_service.submit(
                session.id,
                PressType.CRISIS,
                "我们会持续回应市场关切，并明确现金流、组织调整和产品节奏的后续动作。",
                duration_s=90,
            )

        result = await orchestrator.settle_quarter(session.id)
        llm_calls_reported += result.llm_calls

    stored = await company_service.session_repo.get(session.id)
    assert stored is not None
    assert len(stored.history) == 4
    assert stored.status == "won"

    press_archive = await orchestrator.press_archive_repo.list_by_session(session.id)
    assert len(press_archive) == 1
    meta = await company_service.meta_repo.get(player_id)
    assert len(meta.unlocked_legacies) >= 1
    assert llm_calls_reported == 5
    assert spy.call_kinds == ["director", "director", "director", "press_eval", "director"]
    assert http_calls["count"] == 0


def _safe_decision_cards(
    n: int,
    quarter: int,
    current_stats: object | None = None,
    rng_seed: int | None = None,
) -> list[dict[str, object]]:
    cards = [
        build_decision_card(
            id=f"D_SAFE_Q{quarter}",
            category=DecisionCategory.SOOTHE,
            title="稳住团队",
            description="给团队一点修复时间",
            immediate_effect=StatsDelta(CASH=0, MORALE=4, BOARD=1, FACE=1),
            flavor="话术不值钱，真心值",
            long_term_hint=None,
            boomerang_seeds=[],
        ),
        build_decision_card(
            id=f"D_BOARD_Q{quarter}",
            category=DecisionCategory.DELAY_BOARD,
            title="稳住董事",
            description="争取一季缓冲期",
            immediate_effect=StatsDelta(CASH=0, MORALE=1, BOARD=3, FACE=0),
            flavor="耐心是借来的",
            long_term_hint=None,
            boomerang_seeds=[],
        ),
        build_decision_card(
            id=f"D_FACE_Q{quarter}",
            category=DecisionCategory.NEGOTIATE_RIVAL,
            title="谈个缓冲",
            description="试着把竞争变成合作",
            immediate_effect=StatsDelta(CASH=1, MORALE=1, BOARD=1, FACE=2),
            flavor="桌上谈判，桌下拔刀",
            long_term_hint=None,
            boomerang_seeds=[],
        ),
    ]
    return [card.model_dump(mode="json") for card in cards[:n]]
