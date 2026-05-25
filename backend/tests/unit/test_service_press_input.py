"""Tests for the press input service."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from app.domain import MemoryWindow, PressInput, PressType, QuarterPhase
from app.repo.memory_impl import InMemoryGameSessionRepo
from app.repo.protocols import GameSession
from app.services.press_input_service import (
    InvalidPressPhase,
    PressInputService,
    TranscriptRejected,
    WrongPressQuarter,
)
from app.services.quarter_state_machine import QuarterStateMachine
from tests.factories import build_company, build_employee, build_quarter, build_stats


def _build_session(
    *,
    session_id: str = "S-press-1",
    quarter_number: int = 3,
    phase: QuarterPhase = QuarterPhase.PRESS,
    press_input: PressInput | None = None,
) -> GameSession:
    now = datetime(2026, 5, 23, 9, 0, tzinfo=UTC)
    quarter = build_quarter(number=quarter_number, phase=phase, press_input=press_input)
    return GameSession(
        id=session_id,
        player_id="player-1",
        company=build_company(),
        stats=build_stats(),
        quarter=quarter,
        employees=[build_employee()],
        history=[],
        promise_log=[],
        agent_memory=MemoryWindow(entries=[]),
        scheduled_events=[],
        status="active",
        created_at=now,
        updated_at=now,
    )


@pytest.mark.asyncio
async def test_submit_rejects_wrong_quarter() -> None:
    repo = InMemoryGameSessionRepo()
    session = await repo.create(_build_session(quarter_number=2))
    service = PressInputService(repo)
    transcript = "有效 transcript 内容足够长可以通过检查。"

    with pytest.raises(WrongPressQuarter):
        await service.submit(session.id, PressType.CRISIS, transcript)


@pytest.mark.asyncio
async def test_submit_rejects_wrong_phase() -> None:
    repo = InMemoryGameSessionRepo()
    session = await repo.create(_build_session(phase=QuarterPhase.DECISION))
    service = PressInputService(repo)

    with pytest.raises(InvalidPressPhase):
        await service.submit(
            session.id,
            PressType.CRISIS,
            "有效 transcript 内容足够长可以通过检查。",
        )


@pytest.mark.asyncio
async def test_submit_rejected_transcript_does_not_change_session() -> None:
    repo = InMemoryGameSessionRepo()
    session = await repo.create(_build_session())
    service = PressInputService(repo)
    before = await repo.get(session.id)
    assert before is not None

    with pytest.raises(TranscriptRejected):
        await service.submit(
            session.id,
            PressType.CRISIS,
            "这段话里包含 PB_001，所以应该被整段拒绝。这个长度也足够长。",
        )

    after = await repo.get(session.id)
    assert after is not None
    assert after.quarter.press_input is None
    assert after == before


@pytest.mark.asyncio
async def test_submit_persists_cleaned_press_input_and_flags() -> None:
    repo = InMemoryGameSessionRepo()
    session = await repo.create(_build_session())
    service = PressInputService(repo)

    result = await service.submit(
        session.id,
        PressType.CRISIS,
        "我们正在和Google讨论合作，并且会继续推动产品和组织调整，确保沟通一致。",
        duration_s=88.5,
    )

    assert result.accepted is True
    assert result.flags == ["brand_replaced"]
    assert result.replaced_count == 1
    assert result.press_input_quarter == 3

    persisted = await repo.get(session.id)
    assert persisted is not None
    assert persisted.quarter.press_input is not None
    assert persisted.quarter.press_input.transcript.count("[品牌]") == 1
    assert persisted.quarter.press_input.flags == ["brand_replaced"]
    assert persisted.quarter.press_input.quarter == 3


@pytest.mark.asyncio
async def test_submit_with_state_machine_enters_settlement_phase() -> None:
    repo = InMemoryGameSessionRepo()
    session = await repo.create(_build_session())
    service = PressInputService(repo, state_machine=QuarterStateMachine(repo))

    await service.submit(
        session.id,
        PressType.CRISIS,
        "我们会说明现金流和组织安排，并且会持续回应外界质疑，保证所有调整都能按计划执行。",
    )

    persisted = await repo.get(session.id)
    assert persisted is not None
    assert persisted.quarter.phase == QuarterPhase.SETTLEMENT
