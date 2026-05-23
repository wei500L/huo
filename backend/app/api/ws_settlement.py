"""Websocket settlement background tasks."""

from __future__ import annotations

import asyncio

from app.api.ws_connection import _map_exception, _send, _toast, _wrap_outbound
from app.protocol import SettlementBundle, SettleQuarter
from app.services import DeathReportService, SettlementOrchestrator

__all__ = ["queue_settlement"]


async def queue_settlement(
    ack_for: str,
    payload: SettleQuarter,
    player_id: str,
    orchestrator: SettlementOrchestrator,
    death_report_service: DeathReportService,
) -> None:
    await _send(player_id, _toast("settlement_queued", ack_for=ack_for))
    asyncio.create_task(
        _settle_background(
            player_id,
            payload.session_id,
            orchestrator,
            death_report_service,
            ack_for,
        )
    )


async def _settle_background(
    player_id: str,
    session_id: str,
    orchestrator: SettlementOrchestrator,
    death_report_service: DeathReportService,
    ack_for: str,
) -> None:
    try:
        result = await orchestrator.settle_quarter(session_id)
        bundle = SettlementBundle.from_domain(
            session_id=result.session_id,
            quarter_number=result.quarter_number,
            settlement=result.settlement,
            press_bundle=result.press_bundle,
            new_stats=result.new_stats,
            history_added=result.history_added,
            death=result.death_reason,
        )
        await _send(player_id, _wrap_outbound(bundle, ack_for))
        if result.death_reason is not None:
            report = await death_report_service.generate(session_id, result.death_reason)
            await _send(player_id, _wrap_outbound(report, ack_for))
    except Exception as exc:  # noqa: BLE001
        await _send(player_id, _map_exception(exc, ack_for))
