"""REST API routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel, ConfigDict

from app.api.deps import (
    get_company_service,
    get_death_report_service,
    get_decision_service,
    get_gossip_service,
    get_meta_repo,
    get_press_input_service,
    get_quarter_state_machine,
    get_session_repo,
    get_settlement_orchestrator,
)
from app.domain import PressType, QuarterPhase
from app.protocol import (
    CollectGossip,
    CreateGame,
    DeathReportBundle,
    DecisionAck,
    DecisionCardDTO,
    GameSnapshot,
    GossipResult,
    HistoryEntryDTO,
    MetaSummaryDTO,
    PressAck,
    SelectDecision,
    SettlementBundle,
    SettleQuarter,
    SubmitPress,
)
from app.repo.protocols import GameSession, GameSessionRepo, MetaProgressRepo
from app.services import (
    CompanyService,
    DeathReportService,
    DecisionService,
    GossipService,
    PressInputService,
    QuarterStateMachine,
    SessionNotFound,
    SettlementOrchestrator,
)

__all__ = ["router"]

router = APIRouter(prefix="/api/v1", tags=["games"])


class TransitionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    target_phase: QuarterPhase


async def _snapshot_from_session(
    session_id: str,
    session_repo: GameSessionRepo,
    meta_repo: MetaProgressRepo,
) -> GameSnapshot:
    session = await _load_session(session_repo, session_id)
    return GameSnapshot.from_domain(
        session_id=session.id,
        player_id=session.player_id,
        company=session.company,
        stats=session.stats,
        quarter=session.quarter,
        history=session.history,
        meta_progress=await meta_repo.get(session.player_id),
    )


async def _load_session(session_repo: GameSessionRepo, session_id: str) -> GameSession:
    session = await session_repo.get(session_id)
    if session is None:
        raise SessionNotFound(f"session not found: {session_id}")
    return session


async def _gossip_result(
    session_id: str,
    payload: CollectGossip,
    service: GossipService,
    session_repo: GameSessionRepo,
) -> GossipResult:
    lead = await service.collect_gossip(session_id, payload.scene)
    session = await _load_session(session_repo, session_id)
    return GossipResult.from_domain(
        session_id=session_id,
        quarter_number=payload.quarter_number,
        lead=lead,
        ap_remaining=session.quarter.ap_remaining,
    )


async def _decision_ack(
    session_id: str,
    payload: SelectDecision,
    service: DecisionService,
) -> DecisionAck:
    result = await service.select_decision(session_id, payload.card_id)
    return DecisionAck.from_domain(
        session_id=result.session_id,
        quarter_number=payload.quarter_number,
        card_id=result.selected_card_id,
        immediate_stats=result.new_stats,
        next_phase=result.next_phase_hint,
    )


async def _press_ack(
    session_id: str,
    payload: SubmitPress,
    service: PressInputService,
) -> PressAck:
    result = await service.submit(
        session_id,
        PressType(payload.press_type),
        payload.transcript,
        payload.duration_s,
    )
    return PressAck(
        session_id=session_id,
        quarter_number=payload.quarter_number,
        accepted=result.accepted,
        flags=result.flags,
        replaced_count=result.replaced_count,
    )


async def _settlement_bundle(
    session_id: str,
    payload: SettleQuarter,
    orchestrator: SettlementOrchestrator,
) -> SettlementBundle:
    result = await orchestrator.settle_quarter(session_id)
    return SettlementBundle.from_domain(
        session_id=result.session_id,
        quarter_number=payload.quarter_number,
        settlement=result.settlement,
        press_bundle=result.press_bundle,
        new_stats=result.new_stats,
        history_added=result.history_added,
        death=result.death_reason,
    )


@router.post("/games", response_model=GameSnapshot)
async def create_game(
    payload: CreateGame,
    service: CompanyService = Depends(get_company_service),
    session_repo: GameSessionRepo = Depends(get_session_repo),
    meta_repo: MetaProgressRepo = Depends(get_meta_repo),
) -> GameSnapshot:
    session = await service.create_new_run(payload.player_id, payload.request_legacies)
    return await _snapshot_from_session(session.id, session_repo, meta_repo)


@router.post("/games/{session_id}/decisions/draw", response_model=list[DecisionCardDTO])
async def draw_decisions(
    session_id: str,
    service: DecisionService = Depends(get_decision_service),
) -> list[DecisionCardDTO]:
    session = await service.draw_decision_cards(session_id)
    return [DecisionCardDTO.from_domain(card) for card in session.quarter.decision_cards]


@router.post("/games/{session_id}/decisions/select", response_model=DecisionAck)
async def select_decision(
    session_id: str,
    payload: SelectDecision,
    service: DecisionService = Depends(get_decision_service),
) -> DecisionAck:
    return await _decision_ack(session_id, payload, service)


@router.post("/games/{session_id}/gossip", response_model=GossipResult)
async def collect_gossip(
    session_id: str,
    payload: CollectGossip,
    service: GossipService = Depends(get_gossip_service),
    session_repo: GameSessionRepo = Depends(get_session_repo),
) -> GossipResult:
    return await _gossip_result(session_id, payload, service, session_repo)


@router.post("/games/{session_id}/press", response_model=PressAck)
async def submit_press(
    session_id: str,
    payload: SubmitPress,
    service: PressInputService = Depends(get_press_input_service),
) -> PressAck:
    return await _press_ack(session_id, payload, service)


@router.post("/games/{session_id}/settlement", response_model=SettlementBundle)
async def settle_quarter(
    session_id: str,
    payload: SettleQuarter,
    orchestrator: SettlementOrchestrator = Depends(get_settlement_orchestrator),
) -> SettlementBundle:
    return await _settlement_bundle(session_id, payload, orchestrator)


@router.post("/games/{session_id}/state/transition", response_model=GameSnapshot)
async def transition_state(
    session_id: str, payload: TransitionRequest,
    state_machine: QuarterStateMachine = Depends(get_quarter_state_machine),
    session_repo: GameSessionRepo = Depends(get_session_repo),
    meta_repo: MetaProgressRepo = Depends(get_meta_repo),
) -> GameSnapshot:
    await state_machine.transition_to(session_id, payload.target_phase)
    return await _snapshot_from_session(session_id, session_repo, meta_repo)


@router.get("/games/{session_id}", response_model=GameSnapshot)
async def get_game(
    session_id: str,
    session_repo: GameSessionRepo = Depends(get_session_repo),
    meta_repo: MetaProgressRepo = Depends(get_meta_repo),
) -> GameSnapshot:
    return await _snapshot_from_session(session_id, session_repo, meta_repo)


@router.get("/games/{session_id}/history", response_model=list[HistoryEntryDTO])
async def get_history(
    session_id: str,
    session_repo: GameSessionRepo = Depends(get_session_repo),
) -> list[HistoryEntryDTO]:
    session = await _load_session(session_repo, session_id)
    return [HistoryEntryDTO.from_domain(entry) for entry in session.history]


@router.get("/games/{session_id}/death-report", response_model=DeathReportBundle)
async def get_death_report(
    session_id: str,
    service: DeathReportService = Depends(get_death_report_service),
) -> DeathReportBundle:
    return await service.generate(session_id)


@router.get("/players/{player_id}/meta", response_model=MetaSummaryDTO)
async def get_player_meta(
    player_id: str,
    meta_repo: MetaProgressRepo = Depends(get_meta_repo),
) -> MetaSummaryDTO:
    return MetaSummaryDTO.from_domain(await meta_repo.get(player_id))
