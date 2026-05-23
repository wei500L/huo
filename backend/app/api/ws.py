"""WebSocket API."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query, WebSocket

from app.api.deps import WebSocketGatewayDeps, get_websocket_gateway_deps
from app.api.ws_connection import PING_INTERVAL_S, connection_manager
from app.api.ws_handlers import _serve_websocket

__all__ = ("PING_INTERVAL_S", "connection_manager", "router")

router = APIRouter(tags=["ws"])


@router.websocket("/api/v1/ws/{player_id}")
async def websocket_gateway(
    websocket: WebSocket,
    player_id: str,
    session_id: str | None = Query(default=None),
    deps: WebSocketGatewayDeps = Depends(get_websocket_gateway_deps),
) -> None:
    await _serve_websocket(websocket, player_id, session_id, deps)
