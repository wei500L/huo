"""Shared test fixtures."""

from collections.abc import AsyncIterator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app import config as config_module
from app.api import deps as api_deps
from app.config import Settings
from app.llm import MockLLMClient, PromptBuilder
from app.llm.client import _get_llm_client_cached
from app.main import create_app
from app.repo import memory_impl as memory_impl_module
from app.repo.memory_impl import (
    InMemoryAgentMemoryRepo,
    InMemoryGameSessionRepo,
    InMemoryMetaProgressRepo,
    InMemoryPressArchiveRepo,
)
from app.rules.director_resolver import DirectorResolver
from app.rules.press_resolver import PressResolver
from app.services import (
    CompanyService,
    DeathReportService,
    DecisionService,
    GossipService,
    LegacyResolver,
    PressInputService,
    QuarterStateMachine,
    SettlementInputAggregator,
    SettlementOrchestrator,
)

__all__ = []


@pytest.fixture
def test_settings() -> Settings:
    """Return deterministic dev settings."""

    return Settings(
        app_name="yes-boss-backend",
        env="dev",
        log_level="INFO",
        llm_mode="mock",
        llm_endpoint=None,
        llm_api_key=None,
        llm_model=None,
        llm_timeout_ms=15_000,
        settlement_max_concurrency=4,
    )


@pytest.fixture(autouse=True)
def reset_memory_singletons() -> None:
    _reset_shared_state()
    yield
    _reset_shared_state()


@pytest.fixture
def in_memory_repos() -> tuple[
    InMemoryGameSessionRepo,
    InMemoryMetaProgressRepo,
    InMemoryPressArchiveRepo,
    InMemoryAgentMemoryRepo,
]:
    _reset_shared_state()
    return (
        memory_impl_module.get_session_repo(),
        memory_impl_module.get_meta_repo(),
        memory_impl_module.get_press_archive_repo(),
        memory_impl_module.get_agent_memory_repo(),
    )


@pytest.fixture
def mock_llm() -> MockLLMClient:
    return MockLLMClient()


@pytest.fixture
def full_stack(
    in_memory_repos: tuple[
        InMemoryGameSessionRepo,
        InMemoryMetaProgressRepo,
        InMemoryPressArchiveRepo,
        InMemoryAgentMemoryRepo,
    ],
    mock_llm: MockLLMClient,
) -> tuple[
    CompanyService,
    DecisionService,
    GossipService,
    PressInputService,
    SettlementOrchestrator,
    DeathReportService,
    QuarterStateMachine,
]:
    session_repo, meta_repo, press_archive_repo, agent_memory_repo = in_memory_repos
    state_machine = QuarterStateMachine(session_repo)
    company_service = CompanyService(session_repo=session_repo, meta_repo=meta_repo)
    decision_service = DecisionService(session_repo=session_repo, state_machine=state_machine)
    gossip_service = GossipService(session_repo=session_repo)
    press_input_service = PressInputService(
        session_repo=session_repo,
        state_machine=state_machine,
    )
    aggregator = SettlementInputAggregator(
        session_repo=session_repo,
        meta_repo=meta_repo,
        press_archive_repo=press_archive_repo,
    )
    prompt_builder = PromptBuilder()
    orchestrator = SettlementOrchestrator(
        session_repo=session_repo,
        meta_repo=meta_repo,
        press_archive_repo=press_archive_repo,
        agent_memory_repo=agent_memory_repo,
        aggregator=aggregator,
        prompt_builder=prompt_builder,
        llm_client=mock_llm,
        director_resolver=DirectorResolver(),
        press_resolver=PressResolver(),
        state_machine=state_machine,
    )
    death_report_service = DeathReportService(
        session_repo=session_repo,
        meta_repo=meta_repo,
        press_archive_repo=press_archive_repo,
        prompt_builder=prompt_builder,
        llm_client=mock_llm,
        legacy_resolver=LegacyResolver(),
    )
    return (
        company_service,
        decision_service,
        gossip_service,
        press_input_service,
        orchestrator,
        death_report_service,
        state_machine,
    )


@pytest.fixture
def app_factory(monkeypatch: pytest.MonkeyPatch, test_settings: Settings):
    """Return an app built with injected test settings."""

    monkeypatch.setattr(config_module, "get_settings", lambda: test_settings)
    return create_app()


@pytest_asyncio.fixture
async def client(app_factory) -> AsyncIterator[AsyncClient]:
    """Return an async HTTP client for the ASGI app."""

    transport = ASGITransport(app=app_factory)
    async with AsyncClient(transport=transport, base_url="http://testserver") as async_client:
        yield async_client


def _reset_shared_state() -> None:
    memory_impl_module._session_singleton = InMemoryGameSessionRepo()
    memory_impl_module._meta_singleton = InMemoryMetaProgressRepo()
    memory_impl_module._press_singleton = InMemoryPressArchiveRepo()
    memory_impl_module._agent_singleton = InMemoryAgentMemoryRepo()
    api_deps.get_prompt_builder.cache_clear()
    api_deps.get_quarter_state_machine.cache_clear()
    api_deps.get_settlement_orchestrator.cache_clear()
    _get_llm_client_cached.cache_clear()
