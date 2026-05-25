"""Shared LLM client models and error types."""

from __future__ import annotations

from typing import Literal, Protocol, runtime_checkable

from pydantic import BaseModel, ConfigDict

FinishReason = Literal["stop", "length", "tool_calls", "error", "timeout", "abort"]

__all__ = (
    "FinishReason",
    "LLMClient",
    "LLMError",
    "LLMConfigurationError",
    "LLMHttpError",
    "LLMRateLimited",
    "LLMRequest",
    "LLMResponse",
    "LLMSchemaError",
    "LLMTimeoutError",
    "LLMUnauthorized",
)


class LLMRequest(BaseModel):
    model_config = ConfigDict(frozen=True, strict=True)

    system: str
    user: str
    max_tokens: int = 800
    temperature: float = 0.7
    response_format_hint: Literal["json_object", "text"] = "json_object"
    timeout_ms: int = 15_000


class LLMResponse(BaseModel):
    model_config = ConfigDict(frozen=True, strict=True)

    raw_text: str
    input_tokens: int | None = None
    output_tokens: int | None = None
    model: str | None = None
    finish_reason: FinishReason = "stop"
    latency_ms: int | None = None
    attempts: int = 1
    retry_count: int = 0


class LLMError(Exception):
    default_status_code = 0
    default_message = "llm error"
    default_retryable = False

    status_code: int
    message: str
    retryable: bool

    def __init__(
        self,
        status_code: int | None = None,
        message: str | None = None,
        retryable: bool | None = None,
    ) -> None:
        self.status_code = self.default_status_code if status_code is None else status_code
        self.message = self.default_message if message is None else message
        self.retryable = self.default_retryable if retryable is None else retryable
        super().__init__(self.message)

    def __str__(self) -> str:
        return self.message


class LLMTimeoutError(LLMError):
    default_status_code = 408
    default_message = "request timed out"
    default_retryable = True


class LLMConfigurationError(LLMError):
    default_status_code = 500
    default_message = "llm configuration missing"


class LLMHttpError(LLMError):
    default_status_code = 500
    default_message = "upstream http error"


class LLMSchemaError(LLMError):
    default_status_code = 200
    default_message = "invalid llm response schema"


class LLMUnauthorized(LLMError):
    default_status_code = 401
    default_message = "401 unauthorized"


class LLMRateLimited(LLMError):
    default_status_code = 429
    default_message = "429 rate limited"
    default_retryable = True


@runtime_checkable
class LLMClient(Protocol):
    async def chat_complete(self, request: LLMRequest) -> LLMResponse: ...
