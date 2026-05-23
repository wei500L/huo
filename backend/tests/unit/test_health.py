"""Health endpoint tests."""

import pytest


@pytest.mark.asyncio
async def test_health_endpoints(client) -> None:
    health_response = await client.get("/healthz")
    ready_response = await client.get("/readyz")

    health_payload = health_response.json()
    ready_payload = ready_response.json()

    assert health_response.status_code == 200
    assert health_payload["status"] == "ok"
    assert "ts" in health_payload
    assert isinstance(health_payload["components"], dict)
    assert health_payload["components"]["session_repo"] == "ok"
    assert health_payload["components"]["llm_client"] == "mock"
    assert health_payload["components"]["version"] == "0.1.0"

    assert ready_response.status_code == 200
    assert ready_payload["status"] == "ready"
    assert "ts" in ready_payload
    assert isinstance(ready_payload["components"], dict)
