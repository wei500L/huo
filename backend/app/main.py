"""FastAPI application factory."""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import RequestResponseEndpoint
from starlette.responses import Response

from app import config as config_module
from app.api.health import router as health_router

__all__ = ["create_app"]


def create_app() -> FastAPI:
    """Build the backend application."""

    settings = config_module.get_settings()
    app = FastAPI(title=settings.app_name, version="0.1.0")
    app.state.settings = settings

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.middleware("http")
    async def _pass_through(request: Request, call_next: RequestResponseEndpoint) -> Response:
        return await call_next(request)

    @app.on_event("startup")
    async def _startup() -> None:
        """Startup placeholder."""

    @app.on_event("shutdown")
    async def _shutdown() -> None:
        """Shutdown placeholder."""

    app.include_router(health_router)

    @app.get("/")
    async def root() -> dict[str, str]:
        return {"app": settings.app_name, "version": "0.1.0"}

    return app
