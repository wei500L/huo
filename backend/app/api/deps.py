"""FastAPI dependency providers for the API layer."""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache

from fastapi import Depends

from app.config import get_settings
from app.llm import LLMClient, PromptBuilder
from app.llm import get_llm_client as build_llm_client
from app.repo import protocols as repo_protocols
from app.repo.protocols import (
    AgentMemoryRepo,
    GameSessionRepo,
    MetaProgressRepo,
    PressArchiveRepo,
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

__all__ = (
    "get_agent_memory_repo",
    "get_company_service",
    "get_death_report_service",
    "get_decision_service",
    "get_director_resolver",
    "get_gossip_service",
    "get_legacy_resolver",
    "get_llm_client",
    "get_meta_repo",
    "get_press_archive_repo",
    "get_press_input_service",
    "get_press_resolver",
    "get_prompt_builder",
    "get_quarter_state_machine",
    "get_session_repo",
    "get_settlement_input_aggregator",
    "get_settlement_orchestrator",
    "get_websocket_gateway_deps",
)


def get_session_repo() -> GameSessionRepo:
    return repo_protocols.get_session_repo()


def get_meta_repo() -> MetaProgressRepo:
    return repo_protocols.get_meta_repo()


def get_press_archive_repo() -> PressArchiveRepo:
    return repo_protocols.get_press_archive_repo()


def get_agent_memory_repo() -> AgentMemoryRepo:
    return repo_protocols.get_agent_memory_repo()


def get_llm_client() -> LLMClient:
    settings = get_settings()
    return build_llm_client(settings)


@lru_cache(maxsize=1)
def get_prompt_builder() -> PromptBuilder:
    return PromptBuilder()


@lru_cache(maxsize=32)
def get_quarter_state_machine(
    session_repo: GameSessionRepo = Depends(get_session_repo),
) -> QuarterStateMachine:
    return QuarterStateMachine(session_repo)


def get_company_service(
    session_repo: GameSessionRepo = Depends(get_session_repo),
    meta_repo: MetaProgressRepo = Depends(get_meta_repo),
) -> CompanyService:
    return CompanyService(session_repo=session_repo, meta_repo=meta_repo)


def get_decision_service(
    session_repo: GameSessionRepo = Depends(get_session_repo),
    state_machine: QuarterStateMachine = Depends(get_quarter_state_machine),
) -> DecisionService:
    return DecisionService(session_repo=session_repo, state_machine=state_machine)


def get_gossip_service(
    session_repo: GameSessionRepo = Depends(get_session_repo),
) -> GossipService:
    return GossipService(session_repo=session_repo)


def get_press_input_service(
    session_repo: GameSessionRepo = Depends(get_session_repo),
    state_machine: QuarterStateMachine = Depends(get_quarter_state_machine),
) -> PressInputService:
    return PressInputService(session_repo=session_repo, state_machine=state_machine)


def get_director_resolver() -> DirectorResolver:
    return DirectorResolver()


def get_press_resolver() -> PressResolver:
    return PressResolver()


def get_settlement_input_aggregator(
    session_repo: GameSessionRepo = Depends(get_session_repo),
    meta_repo: MetaProgressRepo = Depends(get_meta_repo),
    press_archive_repo: PressArchiveRepo = Depends(get_press_archive_repo),
) -> SettlementInputAggregator:
    return SettlementInputAggregator(
        session_repo=session_repo,
        meta_repo=meta_repo,
        press_archive_repo=press_archive_repo,
    )


@lru_cache(maxsize=32)
def get_settlement_orchestrator(
    session_repo: GameSessionRepo = Depends(get_session_repo),
    meta_repo: MetaProgressRepo = Depends(get_meta_repo),
    press_archive_repo: PressArchiveRepo = Depends(get_press_archive_repo),
    agent_memory_repo: AgentMemoryRepo = Depends(get_agent_memory_repo),
    aggregator: SettlementInputAggregator = Depends(get_settlement_input_aggregator),
    prompt_builder: PromptBuilder = Depends(get_prompt_builder),
    llm_client: LLMClient = Depends(get_llm_client),
    director_resolver: DirectorResolver = Depends(get_director_resolver),
    press_resolver: PressResolver = Depends(get_press_resolver),
    state_machine: QuarterStateMachine = Depends(get_quarter_state_machine),
) -> SettlementOrchestrator:
    return SettlementOrchestrator(
        session_repo=session_repo,
        meta_repo=meta_repo,
        press_archive_repo=press_archive_repo,
        agent_memory_repo=agent_memory_repo,
        aggregator=aggregator,
        prompt_builder=prompt_builder,
        llm_client=llm_client,
        director_resolver=director_resolver,
        press_resolver=press_resolver,
        state_machine=state_machine,
        settings=get_settings(),
    )


def get_legacy_resolver() -> LegacyResolver:
    return LegacyResolver()


def get_death_report_service(
    session_repo: GameSessionRepo = Depends(get_session_repo),
    meta_repo: MetaProgressRepo = Depends(get_meta_repo),
    press_archive_repo: PressArchiveRepo = Depends(get_press_archive_repo),
    prompt_builder: PromptBuilder = Depends(get_prompt_builder),
    llm_client: LLMClient = Depends(get_llm_client),
    legacy_resolver: LegacyResolver = Depends(get_legacy_resolver),
) -> DeathReportService:
    return DeathReportService(
        session_repo=session_repo,
        meta_repo=meta_repo,
        press_archive_repo=press_archive_repo,
        prompt_builder=prompt_builder,
        llm_client=llm_client,
        legacy_resolver=legacy_resolver,
        settings=get_settings(),
    )


@dataclass(slots=True)
class WebSocketGatewayDeps:
    session_repo: GameSessionRepo
    meta_repo: MetaProgressRepo
    company_service: CompanyService
    decision_service: DecisionService
    gossip_service: GossipService
    press_service: PressInputService
    orchestrator: SettlementOrchestrator
    death_report_service: DeathReportService
    state_machine: QuarterStateMachine


def get_websocket_gateway_deps(
    session_repo: GameSessionRepo = Depends(get_session_repo),
    meta_repo: MetaProgressRepo = Depends(get_meta_repo),
    company_service: CompanyService = Depends(get_company_service),
    decision_service: DecisionService = Depends(get_decision_service),
    gossip_service: GossipService = Depends(get_gossip_service),
    press_service: PressInputService = Depends(get_press_input_service),
    orchestrator: SettlementOrchestrator = Depends(get_settlement_orchestrator),
    death_report_service: DeathReportService = Depends(get_death_report_service),
    state_machine: QuarterStateMachine = Depends(get_quarter_state_machine),
) -> WebSocketGatewayDeps:
    return WebSocketGatewayDeps(
        session_repo=session_repo,
        meta_repo=meta_repo,
        company_service=company_service,
        decision_service=decision_service,
        gossip_service=gossip_service,
        press_service=press_service,
        orchestrator=orchestrator,
        death_report_service=death_report_service,
        state_machine=state_machine,
    )
