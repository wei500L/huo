"""Unit tests for CompanyService."""

from __future__ import annotations

import ast
import inspect
from pathlib import Path
from uuid import UUID, uuid4

import pytest

from app.content import ContentRegistryError
from app.domain import LegacyType, QuarterPhase
from app.repo.memory_impl import InMemoryGameSessionRepo, InMemoryMetaProgressRepo
from app.repo.protocols import GameSession
from app.services.company_service import CompanyService
from tests.factories import build_legacy_unlock, build_meta_progress


@pytest.mark.asyncio
async def test_create_new_run_builds_expected_session_shape() -> None:
    session_repo = InMemoryGameSessionRepo()
    meta_repo = InMemoryMetaProgressRepo()
    service = CompanyService(session_repo=session_repo, meta_repo=meta_repo)

    session = await service.create_new_run(player_id=str(uuid4()), rng_seed=42)

    assert session.status == "active"
    assert session.quarter.number == 1
    assert session.quarter.phase == QuarterPhase.BRIEFING
    assert session.quarter.briefing is not None
    assert len(session.quarter.briefing.hidden_risks) in {1, 2}
    assert len(session.employees) == 12
    assert len({employee.id for employee in session.employees}) == 12
    employee_ids = {employee.id for employee in session.employees}
    assert all(
        relationship.target_id in employee_ids
        for employee in session.employees
        for relationship in employee.relationships
    )
    assert all(0 <= value <= 100 for value in session.stats.model_dump().values())


@pytest.mark.asyncio
async def test_legacy_pr_experience_boosts_face_by_at_least_five() -> None:
    session_repo = InMemoryGameSessionRepo()
    meta_repo = InMemoryMetaProgressRepo()
    player_id = str(uuid4())
    await meta_repo.save(
        build_meta_progress(
            player_id=player_id,
            unlocked_legacies=[build_legacy_unlock(type=LegacyType.PR_EXPERIENCE)],
        )
    )
    service = CompanyService(session_repo=session_repo, meta_repo=meta_repo)

    base = await service.create_new_run(player_id=player_id, apply_legacies=False, rng_seed=7)
    boosted = await service.create_new_run(player_id=player_id, apply_legacies=True, rng_seed=7)

    assert boosted.stats.FACE >= base.stats.FACE + 5


@pytest.mark.asyncio
async def test_same_seed_repeats_company_employees_and_stats() -> None:
    session_repo = InMemoryGameSessionRepo()
    meta_repo = InMemoryMetaProgressRepo()
    service = CompanyService(session_repo=session_repo, meta_repo=meta_repo)
    player_id = str(uuid4())

    first = await service.create_new_run(player_id=player_id, rng_seed=99)
    second = await service.create_new_run(player_id=player_id, rng_seed=99)

    assert first.company.model_dump(exclude={"id"}) == second.company.model_dump(exclude={"id"})
    assert _employee_signature(first) == _employee_signature(second)
    assert first.stats == second.stats


@pytest.mark.asyncio
async def test_different_seeds_generate_highly_varied_runs() -> None:
    session_repo = InMemoryGameSessionRepo()
    meta_repo = InMemoryMetaProgressRepo()
    service = CompanyService(session_repo=session_repo, meta_repo=meta_repo)

    signatures: set[tuple[object, ...]] = set()
    for seed in range(10):
        session = await service.create_new_run(player_id=str(uuid4()), rng_seed=seed)
        signatures.add(
            (
                session.company.name,
                session.company.business,
                _employee_signature(session),
                session.stats.CASH,
                session.stats.MORALE,
                session.stats.BOARD,
                session.stats.FACE,
            )
        )

    assert len(signatures) >= 9


@pytest.mark.asyncio
async def test_player_id_none_generates_uuid4_and_persists_meta() -> None:
    session_repo = InMemoryGameSessionRepo()
    meta_repo = InMemoryMetaProgressRepo()
    service = CompanyService(session_repo=session_repo, meta_repo=meta_repo)

    session = await service.create_new_run(rng_seed=123)
    parsed = UUID(session.player_id)

    assert parsed.version == 4
    meta = await meta_repo.get(session.player_id)
    assert meta.player_id == session.player_id


@pytest.mark.asyncio
async def test_content_sampling_failure_raises_registry_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    session_repo = InMemoryGameSessionRepo()
    meta_repo = InMemoryMetaProgressRepo()
    service = CompanyService(session_repo=session_repo, meta_repo=meta_repo)

    def _boom(_: int | None = None) -> dict[str, object]:
        raise RuntimeError("broken registry")

    monkeypatch.setattr("app.services.company_service.sample_company_template", _boom)

    with pytest.raises(ContentRegistryError):
        await service.create_new_run(player_id=str(uuid4()), rng_seed=1)


def test_company_service_has_no_forbidden_runtime_imports_or_call_tokens() -> None:
    source_file = inspect.getsourcefile(CompanyService)
    assert source_file is not None
    source = Path(source_file).read_text(encoding="utf-8")

    for token in ("llm" + "_client", "chat" + "_complete"):
        assert token not in source

    module = ast.parse(source)
    imports: set[str] = set()
    for node in ast.walk(module):
        if isinstance(node, ast.Import):
            imports.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module is not None:
            imports.add(node.module)

    assert not any(name.startswith("app.llm") for name in imports)
    assert not any(name.startswith("app.api") for name in imports)
    assert not any(name.startswith("app.protocol") for name in imports)


def _employee_signature(session: GameSession) -> tuple[tuple[object, ...], ...]:
    id_to_index = {employee.id: index for index, employee in enumerate(session.employees)}
    signature: list[tuple[object, ...]] = []
    for employee in session.employees:
        relationships = tuple(
            sorted(
                (
                    id_to_index[relationship.target_id],
                    relationship.type,
                    relationship.strength,
                )
                for relationship in employee.relationships
            )
        )
        signature.append(
            (
                employee.name,
                employee.role,
                employee.competence,
                employee.loyalty,
                employee.stress,
                employee.personality_tag,
                employee.faction,
                tuple(employee.hidden_secrets),
                employee.attitude_to_player,
                relationships,
            )
        )
    return tuple(signature)
