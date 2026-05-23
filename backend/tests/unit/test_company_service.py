"""Tests for the company bootstrap service."""

from __future__ import annotations

import ast
import inspect
from uuid import UUID

import pytest

import app.services.company_service as company_service_module
from app.domain import LegacyType
from app.repo.memory_impl import InMemoryGameSessionRepo, InMemoryMetaProgressRepo
from app.services.company_service import CompanyService
from tests.factories import build_legacy_unlock, build_meta_progress


@pytest.mark.asyncio
async def test_create_new_run_is_reproducible_with_seed() -> None:
    player_id = str(UUID("12345678-1234-4234-8234-1234567890ab"))
    first = await CompanyService(
        session_repo=InMemoryGameSessionRepo(),
        meta_repo=InMemoryMetaProgressRepo(),
    ).create_new_run(player_id=player_id, rng_seed=42)
    second = await CompanyService(
        session_repo=InMemoryGameSessionRepo(),
        meta_repo=InMemoryMetaProgressRepo(),
    ).create_new_run(player_id=player_id, rng_seed=42)

    assert first == second
    assert UUID(first.company.id).version == 4
    assert len(first.employees) == 12
    assert {employee.id for employee in first.employees} == {
        employee.id for employee in second.employees
    }
    employee_ids = {employee.id for employee in first.employees}
    for employee in first.employees:
        for relationship in employee.relationships:
            assert relationship.target_id in employee_ids


@pytest.mark.asyncio
async def test_create_new_run_persists_generated_player_and_session() -> None:
    session_repo = InMemoryGameSessionRepo()
    meta_repo = InMemoryMetaProgressRepo()
    service = CompanyService(session_repo=session_repo, meta_repo=meta_repo)

    session = await service.create_new_run(rng_seed=7)

    assert UUID(session.player_id).version == 4
    assert await session_repo.get(session.id) == session
    expected_meta = build_meta_progress(player_id=session.player_id)
    assert await meta_repo.get(session.player_id) == expected_meta


@pytest.mark.asyncio
async def test_create_new_run_keeps_player_history_separate() -> None:
    session_repo = InMemoryGameSessionRepo()
    meta_repo = InMemoryMetaProgressRepo()
    service = CompanyService(session_repo=session_repo, meta_repo=meta_repo)
    player_id = str(UUID("12345678-1234-4234-8234-1234567890ab"))

    await service.create_new_run(player_id=player_id, rng_seed=1)
    await service.create_new_run(player_id=player_id, rng_seed=2)
    await service.create_new_run(player_id=player_id, rng_seed=3)

    sessions = await session_repo.list_by_player(player_id)

    assert len(sessions) == 3
    assert len({session.id for session in sessions}) == 3
    assert all(session.player_id == player_id for session in sessions)


@pytest.mark.asyncio
async def test_apply_legacies_adds_face_bonus_for_pr_experience() -> None:
    player_id = str(UUID("12345678-1234-4234-8234-1234567890ab"))
    base_repo = InMemoryMetaProgressRepo()
    boosted_repo = InMemoryMetaProgressRepo()
    await boosted_repo.save(
        build_meta_progress(
            player_id=player_id,
            unlocked_legacies=[build_legacy_unlock(type=LegacyType.PR_EXPERIENCE)],
        )
    )

    without = await CompanyService(
        session_repo=InMemoryGameSessionRepo(),
        meta_repo=base_repo,
    ).create_new_run(player_id=player_id, rng_seed=99, apply_legacies=False)
    with_legacies = await CompanyService(
        session_repo=InMemoryGameSessionRepo(),
        meta_repo=boosted_repo,
    ).create_new_run(player_id=player_id, rng_seed=99, apply_legacies=True)

    assert with_legacies.stats.FACE == without.stats.FACE + 5


@pytest.mark.asyncio
async def test_create_new_run_wraps_content_sampling_failure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    session_repo = InMemoryGameSessionRepo()
    meta_repo = InMemoryMetaProgressRepo()
    service = CompanyService(session_repo=session_repo, meta_repo=meta_repo)

    def _boom(*args: object, **kwargs: object) -> object:
        raise RuntimeError("boom")

    monkeypatch.setattr(company_service_module, "sample_company_template", _boom)

    with pytest.raises(company_service_module.content_registry.ContentRegistryError):
        await service.create_new_run(rng_seed=13)


def test_company_service_imports_do_not_touch_forbidden_modules() -> None:
    source = inspect.getsource(company_service_module)
    tree = ast.parse(source)
    imports = {
        alias.name
        for node in ast.walk(tree)
        if isinstance(node, ast.Import)
        for alias in node.names
    } | {
        node.module
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module is not None
    }
    assert not any(name.startswith("app.llm") for name in imports if name is not None)
    assert not any(name.startswith("app.api") for name in imports if name is not None)
    assert not any(name.startswith("app.protocol") for name in imports if name is not None)
    assert "llm_client" not in source
    assert "chat_complete" not in source
