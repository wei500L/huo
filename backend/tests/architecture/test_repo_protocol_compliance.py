"""Architecture checks for repository protocol compliance."""

from __future__ import annotations

import inspect
from datetime import datetime
from typing import get_type_hints
from uuid import uuid4

import pytest

from app import config as config_module
from app.config import Settings
from app.domain import MediaHeadline, MemoryWindow, PressBundle
from app.repo import memory_impl, protocols, sql_stub
from app.repo.protocols import GameSession
from tests.factories import (
    build_agent_memory,
    build_company,
    build_employee,
    build_meta_progress,
    build_press_evaluation,
    build_press_input,
    build_quarter,
    build_stats,
)


def _build_session() -> GameSession:
    stamp = datetime.utcnow()
    return GameSession(
        id="S-0001",
        player_id="player-1",
        company=build_company(),
        stats=build_stats(),
        quarter=build_quarter(),
        employees=[build_employee()],
        history=[],
        promise_log=[],
        agent_memory=MemoryWindow(entries=[]),
        scheduled_events=[],
        status="active",
        created_at=stamp,
        updated_at=stamp,
    )


def _build_bundle() -> PressBundle:
    return PressBundle(
        input=build_press_input(),
        evaluation=build_press_evaluation(),
        headlines=[
            MediaHeadline(
                outlet="36 氪",
                headline="测试标题",
                tone="neutral",
            ),
        ],
    )


def _assert_protocol_implementation(protocol_cls: type[object], impl_cls: type[object]) -> None:
    for name, protocol_method in inspect.getmembers(protocol_cls, inspect.isfunction):
        if name.startswith("_"):
            continue
        impl_method = getattr(impl_cls, name)
        assert inspect.iscoroutinefunction(protocol_method)
        assert inspect.iscoroutinefunction(impl_method)
        assert inspect.signature(protocol_method) == inspect.signature(impl_method)
        assert get_type_hints(protocol_method) == get_type_hints(impl_method)


def test_inmemory_repos_fully_match_protocols() -> None:
    _assert_protocol_implementation(protocols.GameSessionRepo, memory_impl.InMemoryGameSessionRepo)
    _assert_protocol_implementation(
        protocols.MetaProgressRepo,
        memory_impl.InMemoryMetaProgressRepo,
    )
    _assert_protocol_implementation(
        protocols.PressArchiveRepo,
        memory_impl.InMemoryPressArchiveRepo,
    )
    _assert_protocol_implementation(protocols.AgentMemoryRepo, memory_impl.InMemoryAgentMemoryRepo)


def test_sql_stub_repos_inherit_protocols() -> None:
    assert protocols.GameSessionRepo in sql_stub.SqlGameSessionRepo.__mro__
    assert protocols.MetaProgressRepo in sql_stub.SqlMetaProgressRepo.__mro__
    assert protocols.PressArchiveRepo in sql_stub.SqlPressArchiveRepo.__mro__
    assert protocols.AgentMemoryRepo in sql_stub.SqlAgentMemoryRepo.__mro__


@pytest.mark.asyncio
async def test_sql_stub_methods_raise_not_implemented() -> None:
    session_repo = sql_stub.SqlGameSessionRepo()
    meta_repo = sql_stub.SqlMetaProgressRepo()
    archive_repo = sql_stub.SqlPressArchiveRepo()
    memory_repo = sql_stub.SqlAgentMemoryRepo()

    session = _build_session()
    meta = build_meta_progress(player_id=str(uuid4()))
    bundle = _build_bundle()

    with pytest.raises(NotImplementedError):
        await session_repo.create(session)
    with pytest.raises(NotImplementedError):
        await session_repo.get(session.id)
    with pytest.raises(NotImplementedError):
        await session_repo.save(session)
    with pytest.raises(NotImplementedError):
        await session_repo.list_by_player(session.player_id)
    with pytest.raises(NotImplementedError):
        await session_repo.delete(session.id)

    with pytest.raises(NotImplementedError):
        await meta_repo.get(meta.player_id)
    with pytest.raises(NotImplementedError):
        await meta_repo.save(meta)
    with pytest.raises(NotImplementedError):
        await meta_repo.list_recent_deaths(meta.player_id)

    with pytest.raises(NotImplementedError):
        await archive_repo.append(session.id, bundle)
    with pytest.raises(NotImplementedError):
        await archive_repo.get("P-0000000000")
    with pytest.raises(NotImplementedError):
        await archive_repo.list_by_session(session.id)

    with pytest.raises(NotImplementedError):
        await memory_repo.append(session.player_id, session.id, build_agent_memory())
    with pytest.raises(NotImplementedError):
        await memory_repo.fetch_window(session.player_id)


@pytest.mark.parametrize(
    ("env", "expected_session", "expected_meta", "expected_archive", "expected_memory"),
    [
        (
            "dev",
            memory_impl.InMemoryGameSessionRepo,
            memory_impl.InMemoryMetaProgressRepo,
            memory_impl.InMemoryPressArchiveRepo,
            memory_impl.InMemoryAgentMemoryRepo,
        ),
        (
            "test",
            memory_impl.InMemoryGameSessionRepo,
            memory_impl.InMemoryMetaProgressRepo,
            memory_impl.InMemoryPressArchiveRepo,
            memory_impl.InMemoryAgentMemoryRepo,
        ),
        (
            "prod",
            sql_stub.SqlGameSessionRepo,
            sql_stub.SqlMetaProgressRepo,
            sql_stub.SqlPressArchiveRepo,
            sql_stub.SqlAgentMemoryRepo,
        ),
    ],
)
def test_factories_switch_by_env(
    monkeypatch: pytest.MonkeyPatch,
    env: str,
    expected_session: type[object],
    expected_meta: type[object],
    expected_archive: type[object],
    expected_memory: type[object],
) -> None:
    llm_config = (
        {
            "llm_mode": "openai_compat",
            "llm_endpoint": "https://llm.example.test/v1",
            "llm_api_key": "secret",
            "llm_model": "model-a",
        }
        if env == "prod"
        else {
            "llm_mode": "mock",
            "llm_endpoint": None,
            "llm_api_key": None,
            "llm_model": None,
        }
    )
    settings = Settings(
        app_name="yes-boss-backend",
        env=env,  # type: ignore[arg-type]
        log_level="INFO",
        **llm_config,  # type: ignore[arg-type]
        llm_timeout_ms=15_000,
        settlement_max_concurrency=4,
    )
    monkeypatch.setattr(config_module, "get_settings", lambda: settings)

    assert isinstance(protocols.get_session_repo(), expected_session)
    assert isinstance(protocols.get_meta_repo(), expected_meta)
    assert isinstance(protocols.get_press_archive_repo(), expected_archive)
    assert isinstance(protocols.get_agent_memory_repo(), expected_memory)
