"""Tests for the quarter state machine service."""

from __future__ import annotations

import asyncio
from datetime import datetime

import pytest

from app.domain import DeathReason, Quarter, QuarterPhase, StatsDelta
from app.repo.memory_impl import InMemoryGameSessionRepo
from app.repo.protocols import GameSession
from app.services.quarter_state_machine import (
    IllegalTransitionError,
    QuarterStateMachine,
    WrongQuarterError,
)
from tests.factories import (
    build_company,
    build_employee,
    build_quarter,
    build_settlement,
    build_stats,
)


def _build_session(
    *,
    quarter: Quarter | None = None,
    status: str = "active",
) -> GameSession:
    now = datetime.utcnow()
    return GameSession(
        id="S-0001",
        player_id="player-1",
        company=build_company(),
        stats=build_stats(),
        quarter=quarter or build_quarter(),
        employees=[build_employee()],
        history=[],
        promise_log=[],
        scheduled_events=[],
        status=status,  # type: ignore[arg-type]
        created_at=now,
        updated_at=now,
    )


async def _machine_with_session(session: GameSession) -> tuple[QuarterStateMachine, GameSession]:
    repo = InMemoryGameSessionRepo()
    created = await repo.create(session)
    return QuarterStateMachine(repo), created


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("quarter", "target"),
    [
        (build_quarter(phase=QuarterPhase.BRIEFING), QuarterPhase.GOSSIP),
        (build_quarter(phase=QuarterPhase.GOSSIP), QuarterPhase.DECISION),
        (build_quarter(number=3, phase=QuarterPhase.DECISION), QuarterPhase.PRESS),
        (build_quarter(number=2, phase=QuarterPhase.DECISION), QuarterPhase.SETTLEMENT),
        (build_quarter(number=3, phase=QuarterPhase.PRESS), QuarterPhase.SETTLEMENT),
        (build_quarter(phase=QuarterPhase.SETTLEMENT), QuarterPhase.DONE),
    ],
)
async def test_legal_transitions_do_not_raise(
    quarter: Quarter,
    target: QuarterPhase,
) -> None:
    machine, session = await _machine_with_session(_build_session(quarter=quarter))

    transitioned = await machine.transition_to(session.id, target)

    assert transitioned.quarter.phase == target


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("quarter", "target"),
    [
        (build_quarter(phase=QuarterPhase.BRIEFING), QuarterPhase.DECISION),
        (build_quarter(phase=QuarterPhase.GOSSIP), QuarterPhase.PRESS),
        (build_quarter(number=1, phase=QuarterPhase.DECISION), QuarterPhase.PRESS),
        (build_quarter(number=3, phase=QuarterPhase.DECISION), QuarterPhase.SETTLEMENT),
        (build_quarter(phase=QuarterPhase.PRESS), QuarterPhase.DONE),
        (build_quarter(phase=QuarterPhase.SETTLEMENT), QuarterPhase.BRIEFING),
        (build_quarter(phase=QuarterPhase.DONE), QuarterPhase.GOSSIP),
    ],
)
async def test_illegal_transitions_raise(
    quarter: Quarter,
    target: QuarterPhase,
) -> None:
    machine, session = await _machine_with_session(_build_session(quarter=quarter))

    with pytest.raises(IllegalTransitionError):
        await machine.transition_to(session.id, target)


@pytest.mark.asyncio
@pytest.mark.parametrize("quarter_number", [1, 2, 4])
async def test_enter_press_phase_only_allows_q3(quarter_number: int) -> None:
    machine, session = await _machine_with_session(
        _build_session(quarter=build_quarter(number=quarter_number, phase=QuarterPhase.DECISION))
    )

    with pytest.raises(IllegalTransitionError):
        await machine.enter_press_phase(session.id)


@pytest.mark.asyncio
async def test_enter_press_phase_allows_q3() -> None:
    machine, session = await _machine_with_session(
        _build_session(quarter=build_quarter(number=3, phase=QuarterPhase.DECISION))
    )

    transitioned = await machine.enter_press_phase(session.id)

    assert transitioned.quarter.phase == QuarterPhase.PRESS


@pytest.mark.asyncio
async def test_finish_settlement_marks_bankruptcy_dead() -> None:
    quarter = build_quarter(
        phase=QuarterPhase.SETTLEMENT,
        selected_decision_id="D-CASH",
    )
    session = _build_session(quarter=quarter).model_copy(update={"stats": build_stats(CASH=5)})
    machine, created = await _machine_with_session(session)
    settlement = build_settlement(quarter=1, metrics_delta=StatsDelta(CASH=-10))

    finished, result = await machine.finish_settlement(created.id, settlement)

    assert result.dead is True
    assert result.reason == DeathReason.BANKRUPTCY
    assert finished.status == "dead"
    assert finished.quarter.phase == QuarterPhase.DONE


@pytest.mark.asyncio
async def test_finish_settlement_marks_q4_win_when_alive() -> None:
    quarter = build_quarter(
        number=4,
        phase=QuarterPhase.SETTLEMENT,
        selected_decision_id="D-WIN",
    )
    machine, session = await _machine_with_session(_build_session(quarter=quarter))
    settlement = build_settlement(quarter=4, metrics_delta=StatsDelta())

    finished, result = await machine.finish_settlement(session.id, settlement)

    assert result.won is True
    assert result.dead is False
    assert finished.status == "won"
    assert finished.quarter.number == 4


@pytest.mark.asyncio
async def test_finish_settlement_advances_q1_when_alive() -> None:
    quarter = build_quarter(
        number=1,
        phase=QuarterPhase.SETTLEMENT,
        selected_decision_id="D-NEXT",
    )
    machine, session = await _machine_with_session(_build_session(quarter=quarter))
    settlement = build_settlement(quarter=1, metrics_delta=StatsDelta(CASH=1))

    finished, result = await machine.finish_settlement(session.id, settlement)

    assert result.next_quarter == 2
    assert finished.status == "active"
    assert finished.quarter.number == 2
    assert finished.quarter.phase == QuarterPhase.BRIEFING


@pytest.mark.asyncio
async def test_advance_to_next_quarter_resets_ap_and_enters_briefing() -> None:
    done_quarter = build_quarter(
        number=1,
        phase=QuarterPhase.DONE,
        settlement=build_settlement(quarter=1),
        ap_remaining=0,
    )
    machine, session = await _machine_with_session(_build_session(quarter=done_quarter))

    advanced = await machine.advance_to_next_quarter(session.id)

    assert advanced.quarter.number == 2
    assert advanced.quarter.ap_remaining == Quarter(number=2).ap_remaining
    assert advanced.quarter.phase == QuarterPhase.BRIEFING
    assert advanced.quarter.briefing is not None


@pytest.mark.asyncio
async def test_finish_settlement_wrong_quarter_raises() -> None:
    quarter = build_quarter(number=2, phase=QuarterPhase.SETTLEMENT)
    machine, session = await _machine_with_session(_build_session(quarter=quarter))

    with pytest.raises(WrongQuarterError):
        await machine.finish_settlement(session.id, build_settlement(quarter=1))


@pytest.mark.asyncio
async def test_concurrent_same_session_transition_reloads_latest_state() -> None:
    machine, session = await _machine_with_session(
        _build_session(quarter=build_quarter(phase=QuarterPhase.BRIEFING))
    )

    results = await asyncio.gather(
        machine.transition_to(session.id, QuarterPhase.GOSSIP),
        machine.transition_to(session.id, QuarterPhase.GOSSIP),
        return_exceptions=True,
    )

    successes = [item for item in results if isinstance(item, GameSession)]
    failures = [item for item in results if isinstance(item, IllegalTransitionError)]
    assert len(successes) == 1
    assert len(failures) == 1
    assert successes[0].updated_at > session.updated_at
