"""WebSocket API integration tests."""

from __future__ import annotations

import ast
import asyncio
from pathlib import Path
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.api import ws as ws_module
from app.api.deps import get_company_service
from app.domain import QuarterPhase
from app.protocol import (
    CreateGame,
    Envelope,
    MessageDirection,
    SelectDecision,
    SettleQuarter,
)
from app.repo.protocols import (
    get_meta_repo as repo_get_meta_repo,
)
from app.repo.protocols import (
    get_session_repo as repo_get_session_repo,
)
from tests.factories import build_decision_card
from tests.integration.test_api_rest import _build_session, _StableCompanyService

ROOT = Path(__file__).resolve().parents[2] / "app" / "api"


def _assert_api_architecture() -> None:
    source = (ROOT / "ws.py").read_text(encoding="utf-8")
    assert "app.llm" not in source
    module = ast.parse(source)
    for node in ast.walk(module):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and any(
            isinstance(dec, ast.Call)
            and isinstance(dec.func, ast.Attribute)
            and dec.func.attr == "websocket"
            for dec in node.decorator_list
        ):
            assert node.end_lineno is not None
            assert node.end_lineno - node.lineno + 1 <= 8, node.name


def _inbound_envelope(message: object, type_name: str) -> str:
    return Envelope(
        direction=MessageDirection.INBOUND,
        type=type_name,
        payload=message,
    ).model_dump_json()


def _create_game_payload(player_id: str) -> str:
    return _inbound_envelope(CreateGame(player_id=player_id, request_legacies=False), "create_game")


def _prepare_settlement_session(player_id: str) -> str:
    repo = repo_get_session_repo()
    meta_repo = repo_get_meta_repo()
    base_session = _build_session(player_id)
    session = base_session.model_copy(
        update={
            "quarter": base_session.quarter.model_copy(
                update={
                    "phase": QuarterPhase.SETTLEMENT,
                    "decision_cards": [build_decision_card()],
                    "selected_decision_id": "D_LAYOFF_01",
                }
            ),
        }
    )
    session_id = session.id
    asyncio.run(repo.create(session))
    asyncio.run(meta_repo.get(player_id))
    return session_id


@pytest.mark.usefixtures("app_factory")
def test_websocket_message_flow_and_heartbeats(
    app_factory, monkeypatch: pytest.MonkeyPatch
) -> None:
    app_factory.dependency_overrides[get_company_service] = lambda: _StableCompanyService(
        repo_get_session_repo(),
        repo_get_meta_repo(),
    )
    monkeypatch.setattr(ws_module, "PING_INTERVAL_S", 0.01)

    player_id = str(uuid4())
    with TestClient(app_factory) as client, client.websocket_connect(
        f"/api/v1/ws/{player_id}"
    ) as ws:
        ws.send_text(_create_game_payload(player_id))
        snapshot = ws.receive_json()
        session_id = snapshot["payload"]["sessionId"]
        assert snapshot["type"] == "game_snapshot"
        assert snapshot["ackFor"] is not None

        ws.send_text(
            _inbound_envelope(
                CreateGame(player_id=player_id, request_legacies=False),
                "cretae_game",
            )
        )
        error = ws.receive_json()
        assert error["type"] == "error"

        ping = ws.receive_json()
        assert ping["type"] == "toast"

        ws.send_text(
            _inbound_envelope(
                SelectDecision(
                    session_id=session_id,
                    quarter_number=1,
                    card_id="D_LAYOFF_01",
                ),
                "select_decision",
            )
        )
        response = ws.receive_json()
        assert response["type"] == "error"

    _assert_api_architecture()


@pytest.mark.usefixtures("app_factory")
def test_websocket_settlement_and_reconnect(app_factory) -> None:
    app_factory.dependency_overrides[get_company_service] = lambda: _StableCompanyService(
        repo_get_session_repo(),
        repo_get_meta_repo(),
    )

    player_id = str(uuid4())
    session_id = _prepare_settlement_session(player_id)

    with TestClient(app_factory) as client, client.websocket_connect(
        f"/api/v1/ws/{player_id}?session_id={session_id}"
    ) as ws:
        snapshot = ws.receive_json()
        assert snapshot["type"] == "game_snapshot"
        assert snapshot["payload"]["sessionId"] == session_id

        ws.send_text(
            _inbound_envelope(
                SettleQuarter(session_id=session_id, quarter_number=1),
                "settle_quarter",
            )
        )
        queued = ws.receive_json()
        assert queued["type"] == "settlement_task_update"
        assert queued["payload"]["status"] == "queued"

        running = ws.receive_json()
        assert running["type"] == "settlement_task_update"
        assert running["payload"]["status"] == "running"

        bundle = ws.receive_json()
        assert bundle["type"] == "settlement_bundle"

        snapshot_or_done = ws.receive_json()
        if snapshot_or_done["type"] == "game_snapshot":
            completed = ws.receive_json()
        else:
            completed = snapshot_or_done
        assert completed["type"] == "settlement_task_update"
        assert completed["payload"]["status"] == "completed"

    with TestClient(app_factory) as client, client.websocket_connect(
        f"/api/v1/ws/{player_id}?session_id={session_id}"
    ) as reconnect_ws:
        reconnect_snapshot = reconnect_ws.receive_json()
        assert reconnect_snapshot["type"] == "game_snapshot"
        assert reconnect_snapshot["payload"]["sessionId"] == session_id
