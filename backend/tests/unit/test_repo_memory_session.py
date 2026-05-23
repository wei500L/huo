"""Tests for the in-memory game session repository."""

from __future__ import annotations

import asyncio
from datetime import datetime, timedelta

import pytest

from app.domain import MemoryWindow
from app.repo.memory_impl import InMemoryGameSessionRepo
from app.repo.protocols import GameSession
from tests.factories import build_company, build_employee, build_promise, build_quarter, build_stats


def _build_session(
    *,
    session_id: str = "S-0001",
    player_id: str = "player-1",
    created_at: datetime | None = None,
    updated_at: datetime | None = None,
) -> GameSession:
    now = datetime.utcnow()
    stamp = created_at or now
    refreshed = updated_at or stamp
    return GameSession(
        id=session_id,
        player_id=player_id,
        company=build_company(),
        stats=build_stats(),
        quarter=build_quarter(),
        employees=[build_employee()],
        history=[],
        promise_log=[build_promise()],
        agent_memory=MemoryWindow(entries=[]),
        scheduled_events=[],
        status="active",
        created_at=stamp,
        updated_at=refreshed,
    )


@pytest.mark.asyncio
async def test_create_and_get_roundtrip() -> None:
    repo = InMemoryGameSessionRepo()
    session = _build_session()

    created = await repo.create(session)
    loaded = await repo.get(session.id)

    assert created == session
    assert loaded == session
    assert loaded is not session


@pytest.mark.asyncio
async def test_save_refreshes_updated_at() -> None:
    repo = InMemoryGameSessionRepo()
    session = _build_session(
        updated_at=datetime.utcnow() - timedelta(days=1),
    )

    saved = await repo.save(session)

    assert saved.updated_at > session.updated_at
    assert (await repo.get(session.id)) == saved


@pytest.mark.asyncio
async def test_list_by_player_filters_correctly() -> None:
    repo = InMemoryGameSessionRepo()
    first = _build_session(
        session_id="S-0001",
        player_id="player-a",
        created_at=datetime(2026, 5, 23, 9, 0, 0),
        updated_at=datetime(2026, 5, 23, 9, 0, 0),
    )
    second = _build_session(
        session_id="S-0002",
        player_id="player-b",
        created_at=datetime(2026, 5, 23, 9, 1, 0),
        updated_at=datetime(2026, 5, 23, 9, 1, 0),
    )
    third = _build_session(
        session_id="S-0003",
        player_id="player-a",
        created_at=datetime(2026, 5, 23, 9, 2, 0),
        updated_at=datetime(2026, 5, 23, 9, 2, 0),
    )

    await repo.create(first)
    await repo.create(second)
    await repo.create(third)

    sessions = await repo.list_by_player("player-a", limit=20)

    assert [session.id for session in sessions] == ["S-0003", "S-0001"]
    assert all(session.player_id == "player-a" for session in sessions)


@pytest.mark.asyncio
async def test_delete_returns_true_then_false() -> None:
    repo = InMemoryGameSessionRepo()
    session = _build_session()

    await repo.create(session)

    assert await repo.delete(session.id) is True
    assert await repo.delete(session.id) is False
    assert await repo.get(session.id) is None


@pytest.mark.asyncio
async def test_concurrent_save_same_session_keeps_record_intact() -> None:
    repo = InMemoryGameSessionRepo()
    session = _build_session()

    await asyncio.gather(*(repo.save(session.model_copy(deep=True)) for _ in range(100)))
    loaded = await repo.get(session.id)
    sessions = await repo.list_by_player(session.player_id)

    assert loaded is not None
    assert loaded.id == session.id
    assert loaded.player_id == session.player_id
    assert loaded.company == session.company
    assert loaded.stats == session.stats
    assert loaded.quarter == session.quarter
    assert len(sessions) == 1
