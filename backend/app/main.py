"""FastAPI application factory."""

from __future__ import annotations

import logging
from time import perf_counter

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from pydantic import ValidationError
from starlette.middleware.base import RequestResponseEndpoint
from starlette.responses import JSONResponse, Response

from app import config as config_module
from app.api.health import router as health_router
from app.api.rest import router as rest_router
from app.api.ws import router as ws_router
from app.llm import LLMConfigurationError, LLMError, LLMTimeoutError
from app.protocol import ErrorOutbound
from app.services import (
    CardNotInDraw,
    DeathReportLLMError,
    DeathReportParseError,
    DecisionNotFound,
    GossipServiceError,
    IllegalTransitionError,
    InsufficientAP,
    InvalidPhaseForDecision,
    InvalidPhaseForGossip,
    InvalidPressPhase,
    InvalidTerminalSession,
    NotInSettlementPhase,
    PressInputServiceError,
    SessionNotFound,
    SettlementError,
    StateMachineError,
    TranscriptRejected,
    WrongPressQuarter,
)

__all__ = ["create_app"]

logger = logging.getLogger(__name__)
_CORS_REGEX = r"^(null|file://.*|https?://localhost(:\d+)?|https?://127\.0\.0\.1(:\d+)?)$"


def create_app() -> FastAPI:
    settings = config_module.get_settings()
    app = FastAPI(title=settings.app_name, version="0.1.0")
    app.state.settings = settings

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["null"],
        allow_origin_regex=_CORS_REGEX,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.middleware("http")
    async def _log_http(request: Request, call_next: RequestResponseEndpoint) -> Response:
        start = perf_counter()
        status_code = 500
        try:
            response = await call_next(request)
            status_code = response.status_code
            return response
        finally:
            latency_ms = max(0, round((perf_counter() - start) * 1000))
            logger.info(
                "http_request",
                extra={
                    "method": request.method,
                    "path": request.url.path,
                    "status": status_code,
                    "latency_ms": latency_ms,
                },
            )

    _register_exception_handlers(app)
    app.include_router(health_router)
    app.include_router(rest_router)
    app.include_router(ws_router)

    @app.get("/")
    async def root() -> dict[str, str]:
        return {"app": settings.app_name, "version": "0.1.0"}

    return app


def _register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(SessionNotFound, _session_not_found)
    app.add_exception_handler(DecisionNotFound, _session_not_found)
    app.add_exception_handler(CardNotInDraw, _conflict)
    app.add_exception_handler(InvalidTerminalSession, _conflict)
    app.add_exception_handler(IllegalTransitionError, _conflict)
    app.add_exception_handler(NotInSettlementPhase, _conflict)
    app.add_exception_handler(InvalidPhaseForDecision, _conflict)
    app.add_exception_handler(InvalidPhaseForGossip, _conflict)
    app.add_exception_handler(InvalidPressPhase, _conflict)
    app.add_exception_handler(WrongPressQuarter, _conflict)
    app.add_exception_handler(InsufficientAP, _conflict)
    app.add_exception_handler(StateMachineError, _state_machine_error)
    app.add_exception_handler(PressInputServiceError, _press_error)
    app.add_exception_handler(GossipServiceError, _gossip_error)
    app.add_exception_handler(TranscriptRejected, _transcript_rejected)
    app.add_exception_handler(LLMTimeoutError, _llm_timeout)
    app.add_exception_handler(LLMConfigurationError, _llm_configuration)
    app.add_exception_handler(LLMError, _llm_error)
    app.add_exception_handler(SettlementError, _settlement_error)
    app.add_exception_handler(DeathReportLLMError, _death_report_llm_error)
    app.add_exception_handler(DeathReportParseError, _death_report_parse_error)
    app.add_exception_handler(TimeoutError, _settlement_timeout)
    app.add_exception_handler(RequestValidationError, _validation_error)
    app.add_exception_handler(ValidationError, _validation_error)
    app.add_exception_handler(Exception, _internal_error)


def _session_not_found(_: Request, exc: Exception) -> JSONResponse:
    return _json_error(404, "session_not_found", "session not found", False)


def _conflict(_: Request, exc: Exception) -> JSONResponse:
    return _json_error(409, _error_code(exc), str(exc) or "conflict", False)


def _press_error(_: Request, exc: Exception) -> JSONResponse:
    status = 404 if "session not found" in str(exc).lower() else 409
    return _json_error(status, _error_code(exc), str(exc) or "press error", False)


def _gossip_error(_: Request, exc: Exception) -> JSONResponse:
    status = 404 if "session not found" in str(exc).lower() else 409
    return _json_error(status, _error_code(exc), str(exc) or "gossip error", False)


def _state_machine_error(_: Request, exc: Exception) -> JSONResponse:
    status = 404 if "session not found" in str(exc).lower() else 409
    return _json_error(status, _error_code(exc), str(exc) or "state machine error", False)


def _transcript_rejected(_: Request, exc: Exception) -> JSONResponse:
    flags = exc.flags if isinstance(exc, TranscriptRejected) else []
    return _json_error(400, "transcript_rejected", "transcript rejected", False, flags)


def _llm_timeout(_: Request, exc: Exception) -> JSONResponse:
    return _json_error(503, "llm_timeout", str(exc), True)


def _llm_configuration(_: Request, exc: Exception) -> JSONResponse:
    return _json_error(500, "llm_configuration_missing", str(exc), False)


def _llm_error(_: Request, exc: Exception) -> JSONResponse:
    retryable = exc.retryable if isinstance(exc, LLMError) else False
    return _json_error(503, _error_code(exc), str(exc), retryable)


def _settlement_error(_: Request, exc: Exception) -> JSONResponse:
    retryable = exc.retryable if isinstance(exc, SettlementError) else False
    code = exc.error_type if isinstance(exc, SettlementError) else _error_code(exc)
    return _json_error(503, code, str(exc), retryable)


def _death_report_llm_error(_: Request, exc: Exception) -> JSONResponse:
    return _json_error(503, "death_report_llm_failed", str(exc), True)


def _death_report_parse_error(_: Request, exc: Exception) -> JSONResponse:
    return _json_error(503, "death_report_parse_failed", str(exc), True)


def _settlement_timeout(_: Request, exc: Exception) -> JSONResponse:
    return _json_error(503, "settlement_timeout", "settlement timed out", True)


def _validation_error(_: Request, exc: Exception) -> JSONResponse:
    return _json_error(422, "validation_error", "invalid request", False)


def _internal_error(_: Request, exc: Exception) -> JSONResponse:
    logger.error("unhandled exception", exc_info=(type(exc), exc, exc.__traceback__))
    return _json_error(500, "internal_error", "internal server error", False)


def _json_error(
    status_code: int,
    code: str,
    message: str,
    retryable: bool,
    flags: list[str] | None = None,
) -> JSONResponse:
    payload = ErrorOutbound(code=code, message=message, retryable=retryable, flags=flags or [])
    return JSONResponse(
        status_code=status_code, content=payload.model_dump(mode="json", by_alias=True)
    )


def _error_code(exc: Exception) -> str:
    return exc.__class__.__name__.lower()
