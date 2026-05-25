"""Early death service integration loop."""

from __future__ import annotations

from uuid import uuid4

import httpx
import pytest

from app.domain import DecisionCategory, QuarterPhase, StatsDelta
from tests.factories import (
    build_death_report_raw,
    build_decision_card,
    build_director_raw,
    build_stats,
)
from tests.llm_spy import SpyLLMClient, raw_json


@pytest.mark.asyncio
async def test_full_loop_death_generates_death_report_and_persists_meta(
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
        _death_decision_cards,
    )
    (
        company_service,
        decision_service,
        gossip_service,
        _press_input_service,
        orchestrator,
        death_report_service,
        state_machine,
    ) = full_stack
    spy = SpyLLMClient(
        {
            "director": raw_json(
                build_director_raw(
                    seed=9,
                    metricsDelta={"CASH": 0, "MORALE": 0, "BOARD": 0, "FACE": 0},
                    rivalAction={"expectedDamage": {"CASH": 0, "MORALE": 0, "BOARD": 0, "FACE": 0}},
                )
            ),
            "death_report": raw_json(build_death_report_raw(seed=9)),
        }
    )
    orchestrator.llm_client = spy
    death_report_service.llm_client = spy

    player_id = str(uuid4())
    session = await company_service.create_new_run(player_id=player_id, rng_seed=909)
    session = session.model_copy(
        update={"stats": build_stats(CASH=75, MORALE=65, BOARD=75, FACE=75)}
    )
    await company_service.session_repo.save(session)

    await state_machine.transition_to(session.id, QuarterPhase.GOSSIP)
    await gossip_service.collect_gossip(session.id, "tearoom", rng_seed=1)
    await state_machine.transition_to(session.id, QuarterPhase.DECISION)
    q1_drawn = await decision_service.draw_decision_cards(session.id, rng_seed=1)
    q1_card = q1_drawn.quarter.decision_cards[0]
    assert q1_card.category == DecisionCategory.LAYOFF
    assert q1_card.immediate_effect.MORALE == -50
    await decision_service.select_decision(session.id, q1_card.id, rng_seed=1)
    q1_result = await orchestrator.settle_quarter(session.id)
    assert q1_result.death_reason is None

    after_q1 = await company_service.session_repo.get(session.id)
    assert after_q1 is not None
    assert after_q1.stats.MORALE == 15
    assert after_q1.quarter.number == 2

    await state_machine.transition_to(session.id, QuarterPhase.GOSSIP)
    await gossip_service.collect_gossip(session.id, "tearoom", rng_seed=2)
    await state_machine.transition_to(session.id, QuarterPhase.DECISION)
    q2_drawn = await decision_service.draw_decision_cards(session.id, rng_seed=2)
    q2_card = q2_drawn.quarter.decision_cards[0]
    await decision_service.select_decision(session.id, q2_card.id, rng_seed=2)
    q2_result = await orchestrator.settle_quarter(session.id)
    assert q2_result.death_reason is not None

    before_meta = await company_service.meta_repo.get(player_id)
    report = await death_report_service.generate(session.id, q2_result.death_reason)
    after_meta = await company_service.meta_repo.get(player_id)

    assert report.obituary
    assert len(report.headlines) == 3
    assert isinstance(report.legacy_unlocks, list)
    assert len(after_meta.death_log) == len(before_meta.death_log) + 1
    assert spy.call_kinds == ["director", "director", "death_report"]
    assert http_calls["count"] == 0


def _death_decision_cards(
    n: int,
    quarter: int,
    current_stats: object | None = None,
    rng_seed: int | None = None,
) -> list[dict[str, object]]:
    if quarter == 1:
        card = build_decision_card(
            id="D_LAYOFF_Q1",
            category=DecisionCategory.LAYOFF,
            title="裁员止血",
            description="一次性压缩团队成本",
            immediate_effect=StatsDelta(CASH=5, MORALE=-50, BOARD=0, FACE=-5),
            flavor="现金流缓了一口，办公室沉了下去",
            long_term_hint=None,
            boomerang_seeds=[],
        )
    else:
        card = build_decision_card(
            id="D_Q2_MORALE_BREAK",
            category=DecisionCategory.HIDE_BAD_NEWS,
            title="继续压住",
            description="继续压住坏消息",
            immediate_effect=StatsDelta(MORALE=-6),
            flavor="沉默不会自动消除坏消息",
            long_term_hint=None,
            boomerang_seeds=[],
        )
    backups = [
        build_decision_card(
            id=f"D_BACKUP_A_Q{quarter}",
            category=DecisionCategory.DELAY_BOARD,
            title="拖住董事",
            description="争取一季缓冲期",
            immediate_effect=StatsDelta(BOARD=2),
            flavor="耐心是借来的",
            long_term_hint=None,
            boomerang_seeds=[],
        ),
        build_decision_card(
            id=f"D_BACKUP_B_Q{quarter}",
            category=DecisionCategory.PRICE_WAR,
            title="降价挤压",
            description="拿价格把对手逼进角落",
            immediate_effect=StatsDelta(CASH=-2, FACE=-2),
            flavor="销量可能上来，利润先下去",
            long_term_hint=None,
            boomerang_seeds=[],
        ),
    ]
    return [item.model_dump(mode="json") for item in [card, *backups][:n]]
