"""Tests for the in-memory meta progress repository."""

from __future__ import annotations

from uuid import uuid4

import pytest

from app.domain import DeathLogEntry, LegacyType, ManagementStyle
from app.repo.memory_impl import InMemoryMetaProgressRepo
from tests.factories import build_legacy_unlock, build_meta_progress


def _death_log_entry(run_id: str, quarter: int) -> DeathLogEntry:
    return DeathLogEntry(
        run_id=run_id,
        company_name="星火集团",
        business="卖月亮咖啡",
        died_at_quarter=quarter,
        death_reason=None,
        obituary=f"Q{quarter} 的结局。",
        biggest_mistake_decision_id=None,
        last_employee_quote=None,
        headlines=[f"Q{quarter} headline"],
    )


@pytest.mark.asyncio
async def test_get_missing_player_returns_default_instance() -> None:
    repo = InMemoryMetaProgressRepo()
    player_id = str(uuid4())

    meta = await repo.get(player_id)

    assert meta.player_id == player_id
    assert meta.schema_version == 1
    assert meta.total_runs == 0
    assert meta.death_log == []


@pytest.mark.asyncio
async def test_save_and_get_roundtrip() -> None:
    repo = InMemoryMetaProgressRepo()
    player_id = str(uuid4())
    meta = build_meta_progress(
        player_id=player_id,
        total_runs=4,
        unlocked_legacies=[build_legacy_unlock(type=LegacyType.ORG_KNOWHOW)],
        unlocked_styles=[ManagementStyle.FACE_KEEPER],
        death_log=[_death_log_entry("R-0001", 4)],
    )

    saved = await repo.save(meta)
    loaded = await repo.get(meta.player_id)

    assert saved == meta
    assert loaded == meta


@pytest.mark.asyncio
async def test_list_recent_deaths_sorts_by_quarter_desc() -> None:
    repo = InMemoryMetaProgressRepo()
    player_id = str(uuid4())
    meta = build_meta_progress(
        player_id=player_id,
        death_log=[
            _death_log_entry("R-0001", 1),
            _death_log_entry("R-0002", 4),
            _death_log_entry("R-0003", 3),
        ],
    )
    await repo.save(meta)

    deaths = await repo.list_recent_deaths(player_id, limit=10)

    assert [entry.died_at_quarter for entry in deaths] == [4, 3, 1]
