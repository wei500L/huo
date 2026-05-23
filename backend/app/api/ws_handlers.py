"""Websocket message routing and receive loop."""

from __future__ import annotations

import asyncio

from fastapi import WebSocket, WebSocketDisconnect
from pydantic import ValidationError

from app.api.deps import WebSocketGatewayDeps
from app.api.ws_connection import (
    _PING_MISS_LIMIT,
    InboundEnvelope,
    _ack_envelope,
    _error_envelope,
    _inbound_message,
    _invalid_message_error,
    _map_exception,
    _ping_envelope,
    _send,
    _send_snapshot,
    _snapshot_for_session,
    _wrap_outbound,
    connection_manager,
)
from app.api.ws_settlement import queue_settlement
from app.domain import PressType
from app.protocol import (
    CollectGossip,
    CreateGame,
    DecisionAck,
    GossipResult,
    MessageDirection,
    Ping,
    PressAck,
    RequestSnapshot,
    SelectDecision,
    SettleQuarter,
    SubmitPress,
)
from app.repo.protocols import GameSessionRepo, MetaProgressRepo
from app.services import (
    CompanyService,
    DeathReportService,
    DecisionService,
    GossipService,
    PressInputService,
    SettlementOrchestrator,
)

__all__ = ["_serve_websocket"]


async def _handle_create_game(
    inbound: InboundEnvelope,
    payload: CreateGame,
    player_id: str,
    session_repo: GameSessionRepo,
    meta_repo: MetaProgressRepo,
    service: CompanyService,
) -> None:
    session = await service.create_new_run(payload.player_id or player_id, payload.request_legacies)
    await connection_manager.bind_session(player_id, session.id)
    await _send_snapshot(player_id, session.id, session_repo, meta_repo, inbound.id)


async def _handle_select_decision(
    inbound: InboundEnvelope,
    payload: SelectDecision,
    player_id: str,
    service: DecisionService,
) -> None:
    result = await service.select_decision(payload.session_id, payload.card_id)
    ack = DecisionAck.from_domain(
        session_id=result.session_id,
        quarter_number=payload.quarter_number,
        card_id=result.selected_card_id,
        immediate_stats=result.new_stats,
        next_phase=result.next_phase_hint,
    )
    await _send(player_id, _wrap_outbound(ack, inbound.id))


async def _handle_collect_gossip(
    inbound: InboundEnvelope,
    payload: CollectGossip,
    player_id: str,
    service: GossipService,
    session_repo: GameSessionRepo,
    meta_repo: MetaProgressRepo,
) -> None:
    lead = await service.collect_gossip(payload.session_id, payload.scene)
    session = await _snapshot_for_session(payload.session_id, session_repo, meta_repo)
    result = GossipResult.from_domain(
        session_id=session.session_id,
        quarter_number=payload.quarter_number,
        lead=lead,
        ap_remaining=session.quarter.ap_remaining,
    )
    await _send(player_id, _wrap_outbound(result, inbound.id))


async def _handle_submit_press(
    inbound: InboundEnvelope,
    payload: SubmitPress,
    player_id: str,
    service: PressInputService,
) -> None:
    result = await service.submit(
        payload.session_id,
        PressType(payload.press_type),
        payload.transcript,
        payload.duration_s,
    )
    ack = PressAck(
        session_id=payload.session_id,
        quarter_number=payload.quarter_number,
        accepted=result.accepted,
        flags=result.flags,
        replaced_count=result.replaced_count,
    )
    await _send(player_id, _wrap_outbound(ack, inbound.id))


async def _handle_request_snapshot(
    inbound: InboundEnvelope,
    payload: RequestSnapshot,
    player_id: str,
    session_repo: GameSessionRepo,
    meta_repo: MetaProgressRepo,
) -> None:
    await _send_snapshot(player_id, payload.session_id, session_repo, meta_repo, inbound.id)


async def _handle_ping(inbound: InboundEnvelope, player_id: str) -> None:
    await _send(player_id, _ack_envelope(inbound.id, "pong"))


async def _dispatch_inbound(
    inbound: InboundEnvelope,
    player_id: str,
    session_repo: GameSessionRepo,
    meta_repo: MetaProgressRepo,
    company_service: CompanyService,
    decision_service: DecisionService,
    gossip_service: GossipService,
    press_service: PressInputService,
    orchestrator: SettlementOrchestrator,
    death_report_service: DeathReportService,
) -> None:
    try:
        if inbound.direction != MessageDirection.INBOUND:
            raise ValueError("direction must be INBOUND")
        match inbound.type:
            case "create_game":
                create_payload = CreateGame.model_validate(inbound.payload)
                await _handle_create_game(
                    inbound,
                    create_payload,
                    player_id,
                    session_repo,
                    meta_repo,
                    company_service,
                )
            case "select_decision":
                select_payload = SelectDecision.model_validate(inbound.payload)
                await _handle_select_decision(inbound, select_payload, player_id, decision_service)
            case "collect_gossip":
                gossip_payload = CollectGossip.model_validate(inbound.payload)
                await _handle_collect_gossip(
                    inbound,
                    gossip_payload,
                    player_id,
                    gossip_service,
                    session_repo,
                    meta_repo,
                )
            case "submit_press":
                press_payload = SubmitPress.model_validate(inbound.payload)
                await _handle_submit_press(inbound, press_payload, player_id, press_service)
            case "settle_quarter":
                settlement_payload = SettleQuarter.model_validate(inbound.payload)
                await queue_settlement(
                    inbound.id,
                    settlement_payload,
                    player_id,
                    orchestrator,
                    death_report_service,
                )
            case "request_snapshot":
                snapshot_payload = RequestSnapshot.model_validate(inbound.payload)
                await _handle_request_snapshot(
                    inbound,
                    snapshot_payload,
                    player_id,
                    session_repo,
                    meta_repo,
                )
            case "ping":
                Ping.model_validate(inbound.payload)
                await _handle_ping(inbound, player_id)
            case _:
                await _send(player_id, _invalid_message_error(inbound.id))
    except ValidationError:
        await _send(
            player_id,
            _error_envelope("validation_error", "invalid message payload", False, inbound.id),
        )
    except Exception as exc:  # noqa: BLE001
        await _send(player_id, _map_exception(exc, inbound.id))


async def _serve_websocket(
    websocket: WebSocket,
    player_id: str,
    session_id: str | None,
    deps: WebSocketGatewayDeps,
) -> None:
    from app.api import ws as ws_public

    session_repo = deps.session_repo
    meta_repo = deps.meta_repo
    company_service = deps.company_service
    decision_service = deps.decision_service
    gossip_service = deps.gossip_service
    press_service = deps.press_service
    orchestrator = deps.orchestrator
    death_report_service = deps.death_report_service
    _ = deps.state_machine
    await websocket.accept()
    await connection_manager.on_connect(player_id, websocket, session_id)
    if session_id is not None:
        try:
            await _send_snapshot(player_id, session_id, session_repo, meta_repo)
        except Exception as exc:  # noqa: BLE001
            await _send(player_id, _map_exception(exc))
    idle_misses = 0
    try:
        while True:
            try:
                raw_text = await asyncio.wait_for(
                    websocket.receive_text(),
                    timeout=ws_public.PING_INTERVAL_S,
                )
            except TimeoutError:
                idle_misses += 1
                await _send(player_id, _ping_envelope())
                if idle_misses >= _PING_MISS_LIMIT:
                    await websocket.close(code=1001)
                    break
                continue
            idle_misses = 0
            try:
                inbound = _inbound_message(raw_text)
            except ValidationError:
                await _send(
                    player_id, _error_envelope("validation_error", "invalid envelope", False)
                )
                continue
            await _dispatch_inbound(
                inbound,
                player_id,
                session_repo,
                meta_repo,
                company_service,
                decision_service,
                gossip_service,
                press_service,
                orchestrator,
                death_report_service,
            )
    except WebSocketDisconnect:
        pass
    finally:
        await connection_manager.on_disconnect(player_id)
