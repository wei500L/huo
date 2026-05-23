"""Integration tests for creating a new run."""

from __future__ import annotations

from uuid import uuid4

import pytest

from app.repo.memory_impl import InMemoryGameSessionRepo, InMemoryMetaProgressRepo
from app.services.company_service import CompanyService


@pytest.mark.asyncio
async def test_create_new_run_persists_session_and_can_be_loaded() -> None:
    session_repo = InMemoryGameSessionRepo()
    meta_repo = InMemoryMetaProgressRepo()
    service = CompanyService(session_repo=session_repo, meta_repo=meta_repo)

    session = await service.create_new_run(player_id=str(uuid4()), rng_seed=11)
    stored = await session_repo.get(session.id)

    assert stored == session


@pytest.mark.asyncio
async def test_same_player_can_create_three_sessions_and_list_them() -> None:
    session_repo = InMemoryGameSessionRepo()
    meta_repo = InMemoryMetaProgressRepo()
    service = CompanyService(session_repo=session_repo, meta_repo=meta_repo)
    player_id = str(uuid4())

    created = [
        await service.create_new_run(player_id=player_id, rng_seed=21 + index) for index in range(3)
    ]
    listed = await session_repo.list_by_player(player_id, limit=10)

    assert len(listed) == 3
    assert {session.id for session in listed} == {session.id for session in created}
