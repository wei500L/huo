"""LLM client abstractions and implementations."""

from __future__ import annotations

import asyncio
from functools import lru_cache
from time import perf_counter
from typing import Literal, cast

import httpx
from pydantic import SecretStr

from app.config import Settings

from ._client_types import (
    FinishReason,
    LLMClient,
    LLMError,
    LLMHttpError,
    LLMRateLimited,
    LLMRequest,
    LLMResponse,
    LLMSchemaError,
    LLMTimeoutError,
    LLMUnauthorized,
)
from .fallback import STUB_DEATH_REPORT, STUB_DIRECTOR, STUB_PRESS_EVAL, get_default_stub

__all__ = (
    "LLMClient",
    "LLMError",
    "LLMHttpError",
    "LLMRateLimited",
    "LLMRequest",
    "LLMResponse",
    "LLMSchemaError",
    "LLMTimeoutError",
    "LLMUnauthorized",
    "MockLLMClient",
    "OpenAICompatibleClient",
    "get_llm_client",
    "retry_chat_complete",
)

_JSON_RETRY_SUFFIX = "上次返回非合法 JSON，请只输出 JSON，无任何其他字符。"
_DEFAULT_STUB_FIXTURES = {
    "director": STUB_DIRECTOR,
    "press_eval": STUB_PRESS_EVAL,
    "death_report": STUB_DEATH_REPORT,
}
_ALLOWABLE_FINISH_REASONS = {"stop", "length", "tool_calls", "error", "timeout", "abort"}
_DEFAULT_PROVIDER_PATHS = {
    "deepseek": "/v1/chat/completions",
    "zhipu": "/chat/completions",
    "tongyi": "/v1/chat/completions",
    "kimi": "/v1/chat/completions",
    "doubao": "/chat/completions",
    "custom": "/v1/chat/completions",
}


class MockLLMClient(LLMClient):
    """Deterministic, non-networked LLM client for tests and local runs."""

    def __init__(self, fixtures: dict[str, str] | None = None) -> None:
        merged = dict(_DEFAULT_STUB_FIXTURES)
        if fixtures is not None:
            merged.update(fixtures)
        self._fixtures = merged

    async def chat_complete(self, request: LLMRequest) -> LLMResponse:
        await asyncio.sleep(0.01)
        kind = _infer_prompt_kind(request.system)
        raw_text = self._fixtures.get(kind, get_default_stub(kind))
        return LLMResponse(raw_text=raw_text, finish_reason="stop", latency_ms=10)


class OpenAICompatibleClient(LLMClient):
    """Async client for OpenAI-compatible chat completion endpoints."""

    def __init__(
        self,
        endpoint: str,
        api_key: SecretStr,
        model: str,
        provider: Literal["deepseek", "zhipu", "tongyi", "kimi", "doubao", "custom"] = "custom",
        http_client: httpx.AsyncClient | None = None,
    ) -> None:
        self.endpoint = endpoint.rstrip("/")
        self.api_key = api_key
        self.model = model
        self.provider = provider
        self._http_client = http_client

    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}(endpoint={self.endpoint!r}, model={self.model!r}, "
            f"provider={self.provider!r}, api_key={self.api_key!r})"
        )

    async def chat_complete(self, request: LLMRequest) -> LLMResponse:
        client = self._ensure_http_client()
        url = _completion_url(self.endpoint, self.provider)
        timeout = httpx.Timeout(connect=5, read=request.timeout_ms / 1000, write=5, pool=5)
        headers = {"Authorization": f"Bearer {self.api_key.get_secret_value()}"}
        body: dict[str, object] = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": request.system},
                {"role": "user", "content": request.user},
            ],
            "max_tokens": request.max_tokens,
            "temperature": request.temperature,
        }
        if request.response_format_hint == "json_object":
            body["response_format"] = {"type": "json_object"}

        start = perf_counter()
        try:
            response = await client.post(url, headers=headers, json=body, timeout=timeout)
        except (TimeoutError, httpx.RequestError) as exc:
            raise LLMTimeoutError() from exc
        latency_ms = max(0, round((perf_counter() - start) * 1000))
        status_code = response.status_code
        if status_code == 401:
            raise LLMUnauthorized()
        if status_code == 429:
            raise LLMRateLimited()
        if 500 <= status_code <= 599:
            raise LLMHttpError(
                status_code=status_code,
                message=f"{status_code} {response.reason_phrase.lower()}",
                retryable=True,
            )
        if 400 <= status_code <= 499:
            raise LLMHttpError(
                status_code=status_code,
                message=f"{status_code} {response.reason_phrase.lower()}",
                retryable=False,
            )

        try:
            payload = response.json()
        except ValueError as exc:
            raise LLMSchemaError(message="invalid JSON response", status_code=status_code) from exc
        if not isinstance(payload, dict):
            raise LLMSchemaError(message="invalid JSON response shape", status_code=status_code)

        choices = payload.get("choices")
        if not isinstance(choices, list) or not choices:
            raise LLMSchemaError(message="missing choices", status_code=status_code)

        first_choice = choices[0]
        if not isinstance(first_choice, dict):
            raise LLMSchemaError(message="invalid choice payload", status_code=status_code)
        message = first_choice.get("message")
        if not isinstance(message, dict):
            raise LLMSchemaError(message="missing message payload", status_code=status_code)
        content = message.get("content")
        if not isinstance(content, str):
            raise LLMSchemaError(message="missing message content", status_code=status_code)

        usage = payload.get("usage")
        input_tokens: int | None = None
        output_tokens: int | None = None
        if isinstance(usage, dict):
            input_tokens = _maybe_int(usage.get("prompt_tokens"))
            output_tokens = _maybe_int(usage.get("completion_tokens"))

        response_model = payload.get("model")
        if response_model is not None and not isinstance(response_model, str):
            raise LLMSchemaError(message="invalid model field", status_code=status_code)
        finish_reason = _finish_reason(first_choice.get("finish_reason"))

        return LLMResponse(
            raw_text=content,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            model=response_model or self.model,
            finish_reason=finish_reason,
            latency_ms=latency_ms,
        )

    def _ensure_http_client(self) -> httpx.AsyncClient:
        if self._http_client is None:
            self._http_client = httpx.AsyncClient()
        return self._http_client


async def retry_chat_complete(
    client: LLMClient,
    request: LLMRequest,
    max_attempts: int = 2,
    backoff_base_ms: int = 200,
) -> LLMResponse:
    """Retry retryable failures with an adjusted JSON-only prompt on retry."""

    if max_attempts < 1:
        raise ValueError("max_attempts must be at least 1")

    current_request = request
    for attempt in range(max_attempts):
        try:
            return await client.chat_complete(current_request)
        except LLMError as exc:
            if not exc.retryable or attempt >= max_attempts - 1:
                raise
            await asyncio.sleep(backoff_base_ms * (2**attempt) / 1000)
            current_request = _append_json_retry_suffix(current_request)
    raise RuntimeError("unreachable")


def get_llm_client(settings: Settings) -> LLMClient:
    """Return a cached LLM client implementation for the configured mode."""

    api_key = settings.llm_api_key.get_secret_value() if settings.llm_api_key else ""
    return _get_llm_client_cached(
        settings.llm_mode,
        settings.llm_endpoint or "",
        api_key,
        settings.llm_model or "",
    )


@lru_cache(maxsize=16)
def _get_llm_client_cached(
    llm_mode: Literal["mock", "openai_compat"],
    llm_endpoint: str,
    llm_api_key: str,
    llm_model: str,
) -> LLMClient:
    if llm_mode == "mock":
        return MockLLMClient()
    if not llm_endpoint:
        raise ValueError("llm_endpoint is required for openai_compat mode")
    if not llm_api_key:
        raise ValueError("llm_api_key is required for openai_compat mode")
    if not llm_model:
        raise ValueError("llm_model is required for openai_compat mode")
    return OpenAICompatibleClient(
        endpoint=llm_endpoint,
        api_key=SecretStr(llm_api_key),
        model=llm_model,
    )


def _infer_prompt_kind(system: str) -> Literal["director", "press_eval", "death_report"]:
    lowered = system.lower()
    if "[kind=director]" in lowered or "总导演" in system:
        return "director"
    if "[kind=press_eval]" in lowered or "评估器" in system:
        return "press_eval"
    if "[kind=death_report]" in lowered or "死亡报告生成器" in system:
        return "death_report"
    if "obituary" in lowered:
        return "death_report"
    if "contentCompleteness" in system:
        return "press_eval"
    return "director"


def _append_json_retry_suffix(request: LLMRequest) -> LLMRequest:
    if request.user.endswith(_JSON_RETRY_SUFFIX):
        return request
    return request.model_copy(update={"user": f"{request.user}\n{_JSON_RETRY_SUFFIX}"})


def _completion_url(endpoint: str, provider: str) -> str:
    normalized = endpoint.rstrip("/")
    if normalized.endswith("/chat/completions"):
        return normalized
    suffix = _DEFAULT_PROVIDER_PATHS.get(provider, "/v1/chat/completions")
    if normalized.endswith("/v1") and suffix == "/v1/chat/completions":
        return normalized + "/chat/completions"
    return normalized + suffix


def _maybe_int(value: object) -> int | None:
    return value if isinstance(value, int) else None


def _finish_reason(value: object) -> FinishReason:
    if isinstance(value, str) and value in _ALLOWABLE_FINISH_REASONS:
        return cast(FinishReason, value)
    return "stop"
