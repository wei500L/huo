"""REST API integration tests."""

from __future__ import annotations

import ast
from contextlib import asynccontextmanager
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient

from app.api.deps import get_company_service
from app.domain import (
    Briefing,
    Company,
    DeathCause,
    Employee,
    Faction,
    MemoryWindow,
    Mood,
    PersonalityTag,
    Quarter,
    QuarterPhase,
    Stats,
)
from app.repo.protocols import (
    GameSession,
)
from app.repo.protocols import (
    get_meta_repo as repo_get_meta_repo,
)
from app.repo.protocols import (
    get_session_repo as repo_get_session_repo,
)

ROOT = Path(__file__).resolve().parents[2] / "app" / "api"


@asynccontextmanager
async def _http_client(app):
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://testserver"
    ) as client:
        yield client


class _StableCompanyService:
    def __init__(self, session_repo, meta_repo) -> None:
        self.session_repo = session_repo
        self.meta_repo = meta_repo

    async def create_new_run(
        self,
        player_id: str | None = None,
        apply_legacies: bool = True,
        rng_seed: int | None = None,
    ) -> GameSession:
        player = player_id or str(uuid4())
        session = _build_session(player)
        await self.meta_repo.get(player)
        return await self.session_repo.create(session)


def _build_session(player_id: str) -> GameSession:
    now = datetime.now(UTC)
    company = Company(
        id=str(uuid4()),
        name="星火集团",
        business="卖月亮咖啡",
        absurdity=3,
        founding_motto="先活下去再说",
        death_causes=[
            DeathCause(category="financial", description="现金流断裂后直接停摆"),
            DeathCause(category="trust", description="员工和董事会同时失去信任"),
        ],
        starting_promises=[],
        founded_year=2024,
    )
    employees = [
        Employee(
            id=str(uuid4()),
            name=name,
            role=role,
            competence=80 - index,
            loyalty=85,
            stress=10,
            personality_tag=PersonalityTag.GOOD_PERSON,
            faction=Faction.NEUTRAL,
            relationships=[],
            hidden_secrets=[],
            attitude_to_player=90,
            current_goal=None,
            mood=Mood.HOPEFUL,
        )
        for index, (name, role) in enumerate(
            [("陈砚", "CFO"), ("唐婉", "HR"), ("沈知远", "CTO"), ("林夏", "PM")],
            start=1,
        )
    ]
    quarter = Quarter(
        number=1,
        phase=QuarterPhase.BRIEFING,
        briefing=Briefing(
            quarter=1,
            market_mood="neutral",
            headline_hint="先稳住组织和现金",
            hidden_risks=[],
        ),
        decision_cards=[],
        selected_decision_id=None,
        gossip_collected=[],
        collected_leads=[],
        press_input=None,
        press_bundle=None,
        settlement=None,
        ap_remaining=10,
    )
    return GameSession(
        id=str(uuid4()),
        player_id=player_id,
        company=company,
        stats=Stats(CASH=95, MORALE=95, BOARD=95, FACE=95),
        quarter=quarter,
        employees=employees,
        history=[],
        promise_log=[],
        agent_memory=MemoryWindow(entries=[]),
        scheduled_events=[],
        status="active",
        created_at=now,
        updated_at=now,
    )


def _best_card_id(cards: list[dict[str, object]]) -> str:
    return max(
        cards,
        key=lambda card: sum(
            int((card.get("immediateEffect") or {}).get(key, 0))
            for key in ("cash", "morale", "board", "face")
        ),
    )["id"]  # type: ignore[index]


def _assert_api_architecture() -> None:
    for path in [ROOT / "rest.py"]:
        source = path.read_text(encoding="utf-8")
        assert "app.llm" not in source
        module = ast.parse(source)
        for node in ast.walk(module):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and any(
                isinstance(dec, ast.Call)
                and isinstance(dec.func, ast.Attribute)
                and dec.func.attr in {"get", "post", "websocket"}
                for dec in node.decorator_list
            ):
                assert node.end_lineno is not None
                assert node.end_lineno - node.lineno + 1 <= 8, node.name


@pytest.mark.asyncio
async def test_rest_endpoints_cover_core_flows(app_factory) -> None:
    app_factory.dependency_overrides[get_company_service] = lambda: _StableCompanyService(
        repo_get_session_repo(),
        repo_get_meta_repo(),
    )

    async with _http_client(app_factory) as client:
        create_response = await client.post("/api/v1/games", json={"type": "create_game"})
        assert create_response.status_code == 200
        snapshot = create_response.json()
        session_id = snapshot["sessionId"]
        player_id = snapshot["playerId"]
        assert snapshot["quarter"]["phase"] == "BRIEFING"
        assert snapshot["metaSummary"]["schemaVersion"] == 1

        illegal_select = await client.post(
            f"/api/v1/games/{session_id}/decisions/select",
            json={
                "type": "select_decision",
                "session_id": session_id,
                "quarter_number": 1,
                "card_id": "D_LAYOFF_01",
            },
        )
        assert illegal_select.status_code == 409

        invalid_press = await client.post(
            f"/api/v1/games/{session_id}/press",
            json={
                "type": "submit_press",
                "session_id": session_id,
                "quarter_number": 3,
                "press_type": "CRISIS",
                "transcript": "too short",
            },
        )
        assert invalid_press.status_code == 422

        missing = await client.get("/api/v1/games/not-a-session")
        assert missing.status_code == 404

        await client.post(
            f"/api/v1/games/{session_id}/state/transition", json={"target_phase": "GOSSIP"}
        )
        gossip_response = await client.post(
            f"/api/v1/games/{session_id}/gossip",
            json={
                "type": "collect_gossip",
                "session_id": session_id,
                "quarter_number": 1,
                "scene": "tearoom",
            },
        )
        assert gossip_response.status_code == 200
        await client.post(
            f"/api/v1/games/{session_id}/state/transition", json={"target_phase": "DECISION"}
        )

        for quarter_number in range(1, 5):
            if quarter_number > 1:
                await client.post(
                    f"/api/v1/games/{session_id}/state/transition", json={"target_phase": "GOSSIP"}
                )
                await client.post(
                    f"/api/v1/games/{session_id}/state/transition",
                    json={"target_phase": "DECISION"},
                )
            draw_response = await client.post(f"/api/v1/games/{session_id}/decisions/draw")
            assert draw_response.status_code == 200
            selected_card = _best_card_id(draw_response.json())

            select_response = await client.post(
                f"/api/v1/games/{session_id}/decisions/select",
                json={
                    "type": "select_decision",
                    "session_id": session_id,
                    "quarter_number": quarter_number,
                    "card_id": selected_card,
                },
            )
            assert select_response.status_code == 200

            if quarter_number == 3:
                await client.post(
                    f"/api/v1/games/{session_id}/state/transition", json={"target_phase": "PRESS"}
                )
                press_response = await client.post(
                    f"/api/v1/games/{session_id}/press",
                    json={
                        "type": "submit_press",
                        "session_id": session_id,
                        "quarter_number": 3,
                        "press_type": "CRISIS",
                        "transcript": (
                            "我们会持续回应市场关切，并确保现金流、产品和组织调整同步推进，"
                            "避免短期波动影响长期执行。"
                        ),
                    },
                )
                assert press_response.status_code == 200

            await client.post(
                f"/api/v1/games/{session_id}/state/transition", json={"target_phase": "SETTLEMENT"}
            )
            settle_response = await client.post(
                f"/api/v1/games/{session_id}/settlement",
                json={
                    "type": "settle_quarter",
                    "session_id": session_id,
                    "quarter_number": quarter_number,
                },
            )
            assert settle_response.status_code == 200

        death_report = await client.get(f"/api/v1/games/{session_id}/death-report")
        assert death_report.status_code == 200
        assert death_report.json()["sessionId"] == session_id

        history = await client.get(f"/api/v1/games/{session_id}/history")
        assert history.status_code == 200
        assert len(history.json()) == 4

        meta = await client.get(f"/api/v1/players/{player_id}/meta")
        assert meta.status_code == 200
        assert meta.json()["totalRuns"] == 1

    _assert_api_architecture()
