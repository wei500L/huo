"""Unit tests for DecisionService."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from app.domain import BoomerangSeed, MemoryWindow, QuarterPhase, StatsDelta
from app.repo.memory_impl import InMemoryGameSessionRepo
from app.repo.protocols import GameSession
from app.services.decision_service import (
    CardNotInDraw,
    DecisionService,
    InvalidPhaseForDecision,
)
from app.services.quarter_state_machine import QuarterStateMachine
from tests.factories import (
    build_company,
    build_decision_card,
    build_employee,
    build_quarter,
    build_stats,
)


@pytest.mark.asyncio
async def test_draw_decision_cards_writes_three_cards_to_quarter() -> None:
    repo = InMemoryGameSessionRepo()
    service = _build_service(repo)
    session = await repo.create(_build_session(phase=QuarterPhase.GOSSIP))

    drawn = await service.draw_decision_cards(session.id, rng_seed=42)

    assert len(drawn.quarter.decision_cards) == 3
    persisted = await repo.get(session.id)
    assert persisted is not None
    assert len(persisted.quarter.decision_cards) == 3


@pytest.mark.asyncio
async def test_select_decision_rejects_non_decision_phase() -> None:
    repo = InMemoryGameSessionRepo()
    service = _build_service(repo)
    card = build_decision_card()
    session = await repo.create(
        _build_session(phase=QuarterPhase.GOSSIP, decision_cards=[card]),
    )

    with pytest.raises(InvalidPhaseForDecision):
        await service.select_decision(session.id, card.id, rng_seed=1)


@pytest.mark.asyncio
async def test_select_decision_rejects_card_not_in_draw() -> None:
    repo = InMemoryGameSessionRepo()
    service = _build_service(repo)
    session = await repo.create(
        _build_session(phase=QuarterPhase.DECISION, decision_cards=[build_decision_card()]),
    )

    with pytest.raises(CardNotInDraw):
        await service.select_decision(session.id, "D_NOT_DRAWN", rng_seed=1)


@pytest.mark.asyncio
async def test_select_decision_applies_immediate_effect() -> None:
    repo = InMemoryGameSessionRepo()
    service = _build_service(repo)
    card = build_decision_card(
        immediate_effect=StatsDelta(CASH=-10, MORALE=-5),
        boomerang_seeds=[],
    )
    session = await repo.create(
        _build_session(
            phase=QuarterPhase.DECISION,
            stats_kwargs={"CASH": 45, "MORALE": 50, "BOARD": 50, "FACE": 60},
            decision_cards=[card],
        ),
    )

    result = await service.select_decision(session.id, card.id, rng_seed=1)

    assert result.new_stats.CASH == 35
    assert result.new_stats.MORALE == 45
    assert result.new_stats.BOARD == 50
    assert result.new_stats.FACE == 60
    persisted = await repo.get(session.id)
    assert persisted is not None
    assert persisted.stats == result.new_stats
    assert persisted.quarter.selected_decision_id == card.id


@pytest.mark.asyncio
async def test_select_decision_clamps_immediate_effect_to_stat_bounds() -> None:
    repo = InMemoryGameSessionRepo()
    service = _build_service(repo)
    card = build_decision_card(
        immediate_effect=StatsDelta(CASH=-25, MORALE=25),
        boomerang_seeds=[],
    )
    session = await repo.create(
        _build_session(
            phase=QuarterPhase.DECISION,
            stats_kwargs={"CASH": 10, "MORALE": 90},
            decision_cards=[card],
        ),
    )

    result = await service.select_decision(session.id, card.id, rng_seed=1)

    assert result.new_stats.CASH == 0
    assert result.new_stats.MORALE == 100


@pytest.mark.asyncio
async def test_select_decision_schedules_probability_one_and_skips_zero() -> None:
    repo = InMemoryGameSessionRepo()
    service = _build_service(repo)
    card = build_decision_card(
        boomerang_seeds=[
            BoomerangSeed(
                delay_quarters=1,
                probability=1.0,
                description="董事会追责",
                effect=StatsDelta(BOARD=-5),
            ),
            BoomerangSeed(
                delay_quarters=1,
                probability=0.0,
                description="员工继续流失",
                effect=StatsDelta(MORALE=-5),
            ),
        ],
    )
    session = await repo.create(
        _build_session(phase=QuarterPhase.DECISION, decision_cards=[card]),
    )

    result = await service.select_decision(session.id, card.id, rng_seed=5)

    assert len(result.new_scheduled_event_ids) == 1
    persisted = await repo.get(session.id)
    assert persisted is not None
    assert len(persisted.scheduled_events) == 1
    assert persisted.scheduled_events[0].source_decision_id == card.id
    assert persisted.scheduled_events[0].fire_quarter == 2
    assert persisted.scheduled_events[0].effect_on_fire == StatsDelta(BOARD=-5)


@pytest.mark.asyncio
async def test_select_decision_skips_boomerang_past_quarter_four() -> None:
    repo = InMemoryGameSessionRepo()
    service = _build_service(repo)
    card = build_decision_card(
        boomerang_seeds=[
            BoomerangSeed(
                delay_quarters=2,
                probability=1.0,
                description="太晚才反噬",
                effect=StatsDelta(FACE=-5),
            ),
        ],
    )
    session = await repo.create(
        _build_session(
            quarter_number=3,
            phase=QuarterPhase.DECISION,
            decision_cards=[card],
        ),
    )

    result = await service.select_decision(session.id, card.id, rng_seed=5)

    assert result.new_scheduled_event_ids == []
    persisted = await repo.get(session.id)
    assert persisted is not None
    assert persisted.scheduled_events == []


@pytest.mark.asyncio
async def test_select_decision_extracts_promises_from_card_text() -> None:
    repo = InMemoryGameSessionRepo()
    service = _build_service(repo)
    card = build_decision_card(
        flavor="Q3 GMV 翻倍",
        description="销售增长20%",
        boomerang_seeds=[],
    )
    session = await repo.create(
        _build_session(phase=QuarterPhase.DECISION, decision_cards=[card]),
    )

    result = await service.select_decision(session.id, card.id, rng_seed=5)

    assert len(result.new_promise_ids) > 0
    persisted = await repo.get(session.id)
    assert persisted is not None
    assert len(persisted.promise_log) > 0


@pytest.mark.asyncio
async def test_same_rng_seed_repeats_boomerang_output() -> None:
    first_repo = InMemoryGameSessionRepo()
    second_repo = InMemoryGameSessionRepo()
    card = build_decision_card(
        boomerang_seeds=[
            BoomerangSeed(
                delay_quarters=1,
                probability=0.5,
                description="概率反噬",
                effect=StatsDelta(FACE=-5),
            ),
        ],
    )
    first = await first_repo.create(
        _build_session(session_id="S-first", phase=QuarterPhase.DECISION, decision_cards=[card]),
    )
    second = await second_repo.create(
        _build_session(session_id="S-second", phase=QuarterPhase.DECISION, decision_cards=[card]),
    )

    first_result = await _build_service(first_repo).select_decision(
        first.id,
        card.id,
        rng_seed=1,
    )
    second_result = await _build_service(second_repo).select_decision(
        second.id,
        card.id,
        rng_seed=1,
    )

    assert first_result.new_scheduled_event_ids == second_result.new_scheduled_event_ids
    first_loaded = await first_repo.get(first.id)
    second_loaded = await second_repo.get(second.id)
    assert first_loaded is not None
    assert second_loaded is not None
    assert [
        event.model_dump(exclude={"source_decision_id"})
        for event in first_loaded.scheduled_events
    ] == [
        event.model_dump(exclude={"source_decision_id"})
        for event in second_loaded.scheduled_events
    ]


@pytest.mark.asyncio
async def test_quarter_three_result_points_to_press() -> None:
    repo = InMemoryGameSessionRepo()
    service = _build_service(repo)
    card = build_decision_card(boomerang_seeds=[])
    session = await repo.create(
        _build_session(
            quarter_number=3,
            phase=QuarterPhase.DECISION,
            decision_cards=[card],
        ),
    )

    result = await service.select_decision(session.id, card.id, rng_seed=1)

    assert result.should_enter_press is True
    assert result.next_phase_hint == "PRESS"


def _build_service(repo: InMemoryGameSessionRepo) -> DecisionService:
    return DecisionService(session_repo=repo, state_machine=QuarterStateMachine(repo))


def _build_session(
    *,
    session_id: str = "S-decision",
    quarter_number: int = 1,
    phase: QuarterPhase,
    decision_cards: list[object] | None = None,
    stats_kwargs: dict[str, object] | None = None,
) -> GameSession:
    now = datetime.now(UTC)
    return GameSession(
        id=session_id,
        player_id="player-1",
        company=build_company(),
        stats=build_stats(**(stats_kwargs or {})),
        quarter=build_quarter(
            number=quarter_number,
            phase=phase,
            decision_cards=decision_cards or [],
        ),
        employees=[build_employee()],
        history=[],
        promise_log=[],
        agent_memory=MemoryWindow(entries=[]),
        scheduled_events=[],
        status="active",
        created_at=now,
        updated_at=now,
    )
