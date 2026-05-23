"""Shared test fixtures."""

from collections.abc import AsyncIterator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app import config as config_module
from app.config import Settings
from app.main import create_app

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
