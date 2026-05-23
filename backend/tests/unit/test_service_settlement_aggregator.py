"""Unit tests for SettlementInputAggregator."""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

import pytest
from pydantic import ValidationError

from app.content.press_types import get_press_type_by_id
from app.domain import (
    Briefing,
    HistoryEntry,
    LegacyType,
    MemoryWindow,
    PromiseTarget,
    QuarterPhase,
    Stats,
    StatsDelta,
)
from app.repo.memory_impl import (
    InMemoryGameSessionRepo,
    InMemoryMetaProgressRepo,
    InMemoryPressArchiveRepo,
)
from app.repo.protocols import GameSession
from app.services.settlement_aggregator import (
    NoDecisionSelected,
    NotInSettlementPhase,
    SessionNotFound,
    SettlementInputAggregator,
)
from tests.factories import (
    build_agent_memory,
    build_company,
    build_decision_card,
    build_employee,
    build_gossip_lead,
    build_legacy_unlock,
    build_meta_progress,
    build_press_input,
    build_promise,
    build_quarter,
    build_scheduled_event,
    build_stats,
)


def _inverse_delta(delta: StatsDelta) -> StatsDelta:
    return StatsDelta(
        CASH=-delta.CASH if delta.CASH is not None else None,
        MORALE=-delta.MORALE if delta.MORALE is not None else None,
        BOARD=-delta.BOARD if delta.BOARD is not None else None,
        FACE=-delta.FACE if delta.FACE is not None else None,
    )


def _promise_target(deadline: int) -> PromiseTarget:
    return PromiseTarget(metric="CASH", target_expr="翻倍", deadline_quarter=deadline)


def _build_session(
    *,
    player_id: str,
    phase: QuarterPhase = QuarterPhase.SETTLEMENT,
    selected_decision_id: str | None = "D-CASH",
) -> GameSession:
    now = datetime(2026, 5, 23, 9, 0, tzinfo=UTC)
    decision = build_decision_card(
        id="D-CASH",
        immediate_effect=StatsDelta(CASH=5, MORALE=-4, BOARD=1, FACE=-3),
    )
    quarter = build_quarter(
        number=3,
        phase=phase,
        briefing=Briefing(
            quarter=3,
            market_mood="bear",
            headline_hint="现金流告急",
            hidden_risks=["媒体追问", "董事会翻脸"],
        ),
        decision_cards=[decision],
        selected_decision_id=selected_decision_id,
        collected_leads=[
            build_gossip_lead(id="G-truth", quarter=3, is_truth=True),
            build_gossip_lead(id="G-rumor", quarter=3, is_truth=False),
        ],
        press_input=build_press_input(quarter=3),
    )
    return GameSession(
        id="S-agg-1",
        player_id=player_id,
        company=build_company(),
        stats=build_stats(CASH=40, MORALE=50, BOARD=55, FACE=60),
        quarter=quarter,
        employees=[
            build_employee(hidden_secrets=["知道旧账"], loyalty=10, attitude_to_player=10),
            build_employee(hidden_secrets=["另一段秘密"], loyalty=60),
        ],
        history=[
            HistoryEntry(
                quarter=1,
                decision_id="D-Q1",
                stats_before=Stats(CASH=50, MORALE=55, BOARD=57, FACE=63),
                stats_after=Stats(CASH=45, MORALE=52, BOARD=56, FACE=61),
                settlement_summary="Q1 勉强撑住。",
            ),
            HistoryEntry(
                quarter=2,
                decision_id="D-Q2",
                stats_before=Stats(CASH=45, MORALE=52, BOARD=56, FACE=61),
                stats_after=Stats(CASH=40, MORALE=50, BOARD=55, FACE=60),
                settlement_summary="Q2 开始失血。",
            ),
        ],
        promise_log=[
            build_promise(id="P-active", quarter_made=1, parsed=_promise_target(3)),
            build_promise(id="P-future", quarter_made=1, parsed=_promise_target(4)),
            build_promise(id="P-current", quarter_made=3, parsed=_promise_target(3)),
            build_promise(
                id="P-judged",
                quarter_made=1,
                parsed=_promise_target(3),
                fulfilled=True,
                judged_at_quarter=3,
            ),
        ],
        agent_memory=MemoryWindow(
            entries=[build_agent_memory(id="M-1"), build_agent_memory(id="M-2")],
            max_size=6,
        ),
        scheduled_events=[
            build_scheduled_event(id="SE-now", fire_quarter=3, resolved=False),
            build_scheduled_event(id="SE-done", fire_quarter=3, resolved=True),
            build_scheduled_event(id="SE-future", fire_quarter=4, resolved=False),
        ],
        status="active",
        created_at=now,
        updated_at=now,
    )


async def _service_with_session(
    session: GameSession | None,
    *,
    player_id: str,
) -> tuple[SettlementInputAggregator, InMemoryGameSessionRepo]:
    session_repo = InMemoryGameSessionRepo()
    meta_repo = InMemoryMetaProgressRepo()
    press_repo = InMemoryPressArchiveRepo()
    await meta_repo.save(
        build_meta_progress(
            player_id=player_id,
            unlocked_legacies=[
                build_legacy_unlock(type=LegacyType.PR_EXPERIENCE, effect_summary="PR+5"),
                build_legacy_unlock(type=LegacyType.EMPLOYEE_TRUST, effect_summary="FACE-keep"),
            ],
        )
    )
    if session is not None:
        await session_repo.create(session)
    return SettlementInputAggregator(session_repo, meta_repo, press_repo), session_repo


@pytest.mark.asyncio
async def test_build_success_path_collects_settlement_context() -> None:
    player_id = str(uuid4())
    session = _build_session(player_id=player_id)
    service, _ = await _service_with_session(session, player_id=player_id)

    context = await service.build(session.id)

    expected_press = get_press_type_by_id("CRISIS")
    assert expected_press is not None
    assert context.session_id == session.id
    assert context.player_id == player_id
    assert context.quarter_number == 3
    assert context.stats_after_immediate == session.stats
    assert context.stats_before_immediate == session.stats.apply_delta(
        _inverse_delta(context.immediate_effect_applied),
    )
    assert context.selected_decision.id == "D-CASH"
    assert context.gossip_collected == session.quarter.collected_leads
    assert [lead.is_truth for lead in context.gossip_collected] == [True, False]
    assert context.press_input == session.quarter.press_input
    assert context.press_type == session.quarter.press_input.press_type
    assert context.press_must_answer == expected_press["must_answer_topics"]
    assert [promise.id for promise in context.active_promises] == ["P-active"]
    assert [event.id for event in context.scheduled_events_firing_this_quarter] == ["SE-now"]
    assert context.agent_memory_window.max_size == 6
    assert context.history_summary == ["Q1 勉强撑住。", "Q2 开始失血。"]
    assert all(employee.hidden_secrets == [] for employee in context.employees_snapshot)
    assert context.employees_snapshot[0].is_quitting_risk() is True
    assert context.company_brief["hiddenRisks"] == ["媒体追问", "董事会翻脸"]
    assert context.meta_buff_signature == "PR+5/FACE-keep"
    assert isinstance(context.rng_seed_for_aggregation, int)
    assert isinstance(context.aggregated_at, datetime)


@pytest.mark.asyncio
async def test_build_rejects_non_settlement_phase() -> None:
    player_id = str(uuid4())
    session = _build_session(player_id=player_id, phase=QuarterPhase.DECISION)
    service, _ = await _service_with_session(session, player_id=player_id)

    with pytest.raises(NotInSettlementPhase):
        await service.build(session.id)


@pytest.mark.asyncio
async def test_build_rejects_missing_selected_decision() -> None:
    player_id = str(uuid4())
    session = _build_session(player_id=player_id, selected_decision_id=None)
    service, _ = await _service_with_session(session, player_id=player_id)

    with pytest.raises(NoDecisionSelected):
        await service.build(session.id)


@pytest.mark.asyncio
async def test_build_rejects_missing_session() -> None:
    player_id = str(uuid4())
    service, _ = await _service_with_session(None, player_id=player_id)

    with pytest.raises(SessionNotFound):
        await service.build("missing-session")


@pytest.mark.asyncio
async def test_context_is_frozen() -> None:
    player_id = str(uuid4())
    session = _build_session(player_id=player_id)
    service, _ = await _service_with_session(session, player_id=player_id)
    context = await service.build(session.id)

    with pytest.raises(ValidationError):
        context.quarter_number = 4  # type: ignore[misc]
