"""Health endpoints."""

from datetime import UTC, datetime
from typing import Any

from fastapi import APIRouter, Request

from app import config as config_module
from app.config import Settings

__all__ = ["router"]

router = APIRouter(tags=["health"])


def _components(settings: Settings | None = None) -> dict[str, str]:
    resolved = settings or config_module.get_settings()
    llm_ready = resolved.llm_mode == "mock" or bool(resolved.llm_endpoint)
    return {
        "memory_repo": "ready",
        "llm_client": "ready" if llm_ready else "not_ready",
    }


def _timestamp() -> str:
    return datetime.now(tz=UTC).isoformat()


@router.get("/healthz")
async def healthz() -> dict[str, Any]:
    """Return a basic liveness payload."""

    components = _components()
    return {"status": "ok", "ts": _timestamp(), "components": components}


@router.get("/readyz")
async def readyz(request: Request) -> dict[str, Any]:
    """Return a readiness payload using app state settings."""

    settings = getattr(request.app.state, "settings", None)
    components = _components(settings if isinstance(settings, Settings) else None)
    status = "ready" if all(value == "ready" for value in components.values()) else "not_ready"
    return {"status": status, "ts": _timestamp(), "components": components}
