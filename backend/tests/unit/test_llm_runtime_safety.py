"""Runtime safety tests for production LLM integration paths."""

from __future__ import annotations

import asyncio
from datetime import UTC, datetime

import pytest
from pydantic import SecretStr, ValidationError

from app.api import ws_settlement
from app.config import Settings
from app.domain import QuarterPhase
from app.llm import (
    LLMConfigurationError,
    LLMRateLimited,
    LLMRequest,
    LLMResponse,
    LLMTimeoutError,
    MockLLMClient,
    OpenAICompatibleClient,
    PromptBuilder,
    get_llm_client,
)
from app.protocol import DeathReportBundle, SettleQuarter
from app.repo.memory_impl import (
    InMemoryAgentMemoryRepo,
    InMemoryGameSessionRepo,
    InMemoryMetaProgressRepo,
    InMemoryPressArchiveRepo,
)
from app.rules.director_resolver import DirectorResolver
from app.rules.press_resolver import PressResolver
from app.services import QuarterStateMachine, SettlementInputAggregator
from app.services.settlement_orchestrator import (
    SettlementLLMCallError,
    SettlementOrchestrator,
    SettlementParseError,
    SettlementResolveError,
)
from tests.factories import build_decision_card, build_session


class TimeoutLLMClient:
    async def chat_complete(self, request: LLMRequest) -> LLMResponse:
        raise LLMTimeoutError()


class InvalidJSONLLMClient:
    async def chat_complete(self, request: LLMRequest) -> LLMResponse:
        return LLMResponse(raw_text="not json", finish_reason="stop")


class SlowCountingLLMClient:
    def __init__(self) -> None:
        self.active = 0
        self.max_active = 0

    async def chat_complete(self, request: LLMRequest) -> LLMResponse:
        self.active += 1
        self.max_active = max(self.max_active, self.active)
        await asyncio.sleep(0.05)
        self.active -= 1
        return await MockLLMClient().chat_complete(request)


class FlakyRetryLLMClient:
    def __init__(self) -> None:
        self.calls = 0

    async def chat_complete(self, request: LLMRequest) -> LLMResponse:
        self.calls += 1
        if self.calls == 1:
            raise LLMRateLimited()
        return await MockLLMClient().chat_complete(request)


class ExplodingDirectorResolver(DirectorResolver):
    def resolve(self, ctx, raw):  # type: ignore[no-untyped-def]
        raise RuntimeError("resolver exploded")


def test_prod_settings_reject_mock_and_missing_real_llm_config() -> None:
    with pytest.raises(ValidationError, match="llm_mode=mock"):
        Settings(env="prod", llm_mode="mock")

    with pytest.raises(ValidationError, match="production LLM configuration is incomplete"):
        Settings(env="prod", llm_mode="openai_compat")


def test_llm_client_requires_explicit_real_config_and_limits_mock_to_dev_test() -> None:
    with pytest.raises(LLMConfigurationError, match="llm_endpoint"):
        get_llm_client(Settings(env="dev", llm_mode="openai_compat"))

    client = get_llm_client(Settings(env="test", llm_mode="mock"))
    assert isinstance(client, MockLLMClient)

    prod = Settings(
        env="prod",
        llm_mode="openai_compat",
        llm_endpoint="https://llm.example.test/v1",
        llm_api_key=SecretStr("secret"),
        llm_model="model-a",
    )
    assert isinstance(get_llm_client(prod), OpenAICompatibleClient)


@pytest.mark.asyncio
async def test_settlement_classifies_llm_timeout_parse_error_and_resolver_error() -> None:
    timeout_orchestrator = await _build_orchestrator(TimeoutLLMClient())
    with pytest.raises(SettlementLLMCallError):
        await timeout_orchestrator.settle_quarter(timeout_orchestrator._test_session_id)

    parse_orchestrator = await _build_orchestrator(InvalidJSONLLMClient())
    with pytest.raises(SettlementParseError):
        await parse_orchestrator.settle_quarter(parse_orchestrator._test_session_id)

    resolver_orchestrator = await _build_orchestrator(
        MockLLMClient(),
        director_resolver=ExplodingDirectorResolver(),
    )
    with pytest.raises(SettlementResolveError):
        await resolver_orchestrator.settle_quarter(resolver_orchestrator._test_session_id)


@pytest.mark.asyncio
async def test_settlement_result_exposes_llm_retry_count() -> None:
    llm = FlakyRetryLLMClient()
    orchestrator = await _build_orchestrator(llm)

    result = await orchestrator.settle_quarter(orchestrator._test_session_id)

    assert result.llm_retries == 1
    assert llm.calls == 2


@pytest.mark.asyncio
async def test_settlement_global_concurrency_limit_and_same_session_lock() -> None:
    llm = SlowCountingLLMClient()
    orchestrator_a = await _build_orchestrator(llm, max_concurrency=1, seed=1)
    orchestrator_b = await _build_orchestrator(
        llm,
        max_concurrency=1,
        seed=2,
        repos=orchestrator_a._test_repos,
    )

    await asyncio.gather(
        orchestrator_a.settle_quarter(orchestrator_a._test_session_id),
        orchestrator_a.settle_quarter(orchestrator_b._test_session_id),
    )
    assert llm.max_active == 1

    llm_same = SlowCountingLLMClient()
    same_session_orchestrator = await _build_orchestrator(llm_same, max_concurrency=2, seed=3)
    results = await asyncio.gather(
        same_session_orchestrator.settle_quarter(same_session_orchestrator._test_session_id),
        same_session_orchestrator.settle_quarter(same_session_orchestrator._test_session_id),
        return_exceptions=True,
    )
    assert llm_same.max_active == 1
    assert any(isinstance(item, Exception) for item in results)


@pytest.mark.asyncio
async def test_ws_queue_duplicate_request_sends_failed_status_and_error(monkeypatch) -> None:
    sent = []

    async def fake_send(player_id, envelope):  # type: ignore[no-untyped-def]
        sent.append(envelope)

    monkeypatch.setattr(ws_settlement, "_send", fake_send)
    async with ws_settlement._TASK_GUARD:
        ws_settlement._TASKS.clear()
        ws_settlement._IN_FLIGHT_BY_SESSION.clear()
        record = ws_settlement._TaskRecord(
            task_id="SET-existing",
            session_id="S-duplicate",
            quarter_number=1,
            player_id="P-1",
            ack_for="ack-old",
            queued_at=datetime.now(UTC),
        )
        ws_settlement._TASKS[record.task_id] = record
        ws_settlement._IN_FLIGHT_BY_SESSION[record.session_id] = record.task_id

    await ws_settlement.queue_settlement(
        "ack-new",
        SettleQuarter(session_id="S-duplicate", quarter_number=1),
        "P-1",
        None,  # type: ignore[arg-type]
        None,  # type: ignore[arg-type]
        None,  # type: ignore[arg-type]
        None,  # type: ignore[arg-type]
    )

    assert sent[0].type == "settlement_task_update"
    assert sent[0].payload.status == "failed"
    assert sent[0].payload.error_type == "duplicate_settlement"
    assert sent[1].type == "error"
    assert sent[1].payload.code == "duplicate_settlement"

    async with ws_settlement._TASK_GUARD:
        ws_settlement._TASKS.clear()
        ws_settlement._IN_FLIGHT_BY_SESSION.clear()


@pytest.mark.asyncio
async def test_ws_death_report_task_sends_statuses_and_retry_count(monkeypatch) -> None:
    sent = []

    async def fake_send(player_id, envelope):  # type: ignore[no-untyped-def]
        sent.append(envelope)

    class FakeDeathReportService:
        async def generate(self, session_id, death_reason):  # type: ignore[no-untyped-def]
            return DeathReportBundle(
                session_id=session_id,
                obituary="复盘文本",
                biggest_mistake_decision_id=None,
                headlines=["一", "二", "三"],
                legacy_unlocks=[],
                styles_unlocked=[],
                llm_degraded=False,
                llm_retry_count=1,
            )

    monkeypatch.setattr(ws_settlement, "_send", fake_send)

    await ws_settlement._run_death_report_task(
        "P-1",
        "S-dead",
        2,
        FakeDeathReportService(),  # type: ignore[arg-type]
        None,
        "ack",
    )

    assert [item.type for item in sent] == [
        "settlement_task_update",
        "settlement_task_update",
        "death_report_bundle",
        "settlement_task_update",
    ]
    assert sent[0].payload.prompt_kind == "death_report"
    assert sent[0].payload.status == "queued"
    assert sent[1].payload.status == "running"
    assert sent[3].payload.status == "completed"
    assert sent[3].payload.retry_count == 1


async def _build_orchestrator(
    llm_client,
    *,
    director_resolver: DirectorResolver | None = None,
    max_concurrency: int = 4,
    seed: int = 1,
    repos: tuple[
        InMemoryGameSessionRepo,
        InMemoryMetaProgressRepo,
        InMemoryPressArchiveRepo,
        InMemoryAgentMemoryRepo,
    ]
    | None = None,
) -> SettlementOrchestrator:
    if repos is None:
        repos = (
            InMemoryGameSessionRepo(),
            InMemoryMetaProgressRepo(),
            InMemoryPressArchiveRepo(),
            InMemoryAgentMemoryRepo(),
        )
    session_repo, meta_repo, press_archive_repo, agent_memory_repo = repos
    session = build_session(seed=seed)
    decision = build_decision_card(seed=seed)
    session = session.model_copy(
        update={
            "quarter": session.quarter.model_copy(
                update={
                    "phase": QuarterPhase.SETTLEMENT,
                    "decision_cards": [decision],
                    "selected_decision_id": decision.id,
                }
            )
        }
    )
    await session_repo.create(session)
    await meta_repo.get(session.player_id)
    settings = Settings(
        env="test",
        llm_mode="mock",
        settlement_max_concurrency=max_concurrency,
        llm_allow_fallback=False,
    )
    orchestrator = SettlementOrchestrator(
        session_repo=session_repo,
        meta_repo=meta_repo,
        press_archive_repo=press_archive_repo,
        agent_memory_repo=agent_memory_repo,
        aggregator=SettlementInputAggregator(session_repo, meta_repo, press_archive_repo),
        prompt_builder=PromptBuilder(),
        llm_client=llm_client,
        director_resolver=director_resolver or DirectorResolver(),
        press_resolver=PressResolver(),
        state_machine=QuarterStateMachine(session_repo),
        settings=settings,
    )
    orchestrator._test_session_id = session.id  # type: ignore[attr-defined]
    orchestrator._test_repos = repos  # type: ignore[attr-defined]
    return orchestrator
