"""LLM spy for integration and architecture tests."""

from __future__ import annotations

import json
from typing import Literal

from app.llm import LLMRequest, LLMResponse, get_default_stub

PromptKind = Literal["director", "press_eval", "death_report"]


class SpyLLMClient:
    """Deterministic non-networked LLM client that records every call."""

    def __init__(self, fixtures: dict[PromptKind, str] | None = None) -> None:
        self.fixtures = fixtures or {}
        self.calls: list[LLMRequest] = []

    async def chat_complete(self, request: LLMRequest) -> LLMResponse:
        self.calls.append(request)
        kind = infer_prompt_kind(request.system)
        return LLMResponse(
            raw_text=self.fixtures.get(kind, get_default_stub(kind)),
            finish_reason="stop",
            latency_ms=0,
        )

    @property
    def call_kinds(self) -> list[PromptKind]:
        return [infer_prompt_kind(call.system) for call in self.calls]


def raw_json(payload: dict[str, object]) -> str:
    return json.dumps(payload, ensure_ascii=False, separators=(",", ":"))


def infer_prompt_kind(system: str) -> PromptKind:
    lowered = system.lower()
    if "[kind=death_report]" in lowered or "死亡报告生成器" in system or "obituary" in lowered:
        return "death_report"
    if "[kind=press_eval]" in lowered or "评估器" in system or "contentcompleteness" in lowered:
        return "press_eval"
    return "director"
