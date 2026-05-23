"""Health endpoints."""

from datetime import UTC, datetime
from typing import Any

from fastapi import APIRouter, Request

from app.config import Settings
from app.repo import protocols as repo_protocols

__all__ = ["router"]

router = APIRouter(tags=["health"])


def _components(settings: Settings | None = None) -> dict[str, str]:
    resolved = settings or Settings()
    try:
        _ = repo_protocols.get_session_repo()
        session_repo_status = "ok"
    except Exception:
        session_repo_status = "error"
    return {
        "session_repo": session_repo_status,
        "llm_client": resolved.llm_mode,
        "version": "0.1.0",
    }


def _timestamp() -> str:
    return datetime.now(tz=UTC).isoformat()


@router.get("/healthz")
async def healthz(request: Request) -> dict[str, Any]:
    components = _components(getattr(request.app.state, "settings", None))
    return {"status": "ok", "ts": _timestamp(), "components": components}


@router.get("/readyz")
async def readyz(request: Request) -> dict[str, Any]:
    settings = getattr(request.app.state, "settings", None)
    components = _components(settings if isinstance(settings, Settings) else None)
    status = "ready" if components["session_repo"] == "ok" else "not_ready"
    return {"status": status, "ts": _timestamp(), "components": components}
