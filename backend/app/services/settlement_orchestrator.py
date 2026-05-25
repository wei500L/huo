"""Async settlement orchestration bus."""

from __future__ import annotations

import asyncio
import logging
from collections import Counter
from collections.abc import Awaitable, Callable
from time import perf_counter
from typing import Any

from pydantic import BaseModel, ConfigDict

from app.config import Settings, get_settings
from app.domain import DeathReason, HistoryEntry, PressBundle, Settlement, Stats
from app.llm import (
    STUB_DIRECTOR,
    STUB_PRESS_EVAL,
    LLMClient,
    LLMError,
    LLMRequest,
    ParseError,
    parse_director,
    parse_press_eval,
    retry_chat_complete,
)
from app.llm.prompt_builder import PromptBuilder, PromptBundle
from app.repo.protocols import (
    AgentMemoryRepo,
    GameSessionRepo,
    MetaProgressRepo,
    PressArchiveRepo,
)
from app.rules.director_resolver import DirectorResolution, DirectorResolver
from app.rules.press_resolver import PressResolution, PressResolver
from app.services.quarter_state_machine import QuarterStateMachine
from app.services.settlement_aggregator import (
    SessionNotFound,
    SettlementInputAggregator,
)

logger = logging.getLogger(__name__)

__all__ = (
    "SettlementOrchestrator",
    "SettlementResult",
    "SettlementError",
    "SettlementLLMCallError",
    "SettlementParseError",
    "SettlementResolveError",
)

SettlementStatusCallback = Callable[[str], Awaitable[None]]


class SettlementResult(BaseModel):
    """Outcome of one quarter settlement run."""

    model_config = ConfigDict(frozen=True, strict=True)

    session_id: str
    quarter_number: int
    settlement: Settlement
    press_bundle: PressBundle | None
    new_stats: Stats
    history_added: HistoryEntry
    death_reason: DeathReason | None
    won: bool = False
    llm_degraded: bool = False
    latency_ms: int
    llm_calls: int
    llm_retries: int = 0


class SettlementError(Exception):
    """Base class for settlement orchestration failures."""

    error_type = "settlement_error"
    retryable = False


class SettlementLLMCallError(SettlementError):
    error_type = "llm_call_failed"
    retryable = True

    def __init__(self, prompt_kind: str, exc: Exception) -> None:
        self.prompt_kind = prompt_kind
        self.original = exc
        super().__init__(f"{prompt_kind} LLM call failed: {exc}")


class SettlementParseError(SettlementError):
    error_type = "llm_parse_failed"
    retryable = True

    def __init__(self, prompt_kind: str, exc: Exception) -> None:
        self.prompt_kind = prompt_kind
        self.original = exc
        super().__init__(f"{prompt_kind} LLM output parse failed: {exc}")


class SettlementResolveError(SettlementError):
    error_type = "llm_resolver_failed"
    retryable = False

    def __init__(self, prompt_kind: str, exc: Exception) -> None:
        self.prompt_kind = prompt_kind
        self.original = exc
        super().__init__(f"{prompt_kind} resolver failed: {exc}")


class SettlementOrchestrator:
    """Compose aggregation, LLM calls, resolution, persistence, and terminal state."""

    def __init__(
        self,
        session_repo: GameSessionRepo,
        meta_repo: MetaProgressRepo,
        press_archive_repo: PressArchiveRepo,
        agent_memory_repo: AgentMemoryRepo,
        aggregator: SettlementInputAggregator,
        prompt_builder: PromptBuilder,
        llm_client: LLMClient,
        director_resolver: DirectorResolver,
        press_resolver: PressResolver,
        state_machine: QuarterStateMachine,
        settings: Settings | None = None,
    ) -> None:
        self.settings = settings or get_settings()
        self.session_repo = session_repo
        self.meta_repo = meta_repo
        self.press_archive_repo = press_archive_repo
        self.agent_memory_repo = agent_memory_repo
        self.aggregator = aggregator
        self.prompt_builder = prompt_builder
        self.llm_client = llm_client
        self.director_resolver = director_resolver
        self.press_resolver = press_resolver
        self.state_machine = state_machine
        self._locks: dict[str, asyncio.Lock] = {}
        self._locks_guard = asyncio.Lock()
        self._semaphore = asyncio.Semaphore(max(1, self.settings.settlement_max_concurrency))
        self._failure_counts: Counter[str] = Counter()

    async def settle_quarter(
        self,
        session_id: str,
        status_callback: SettlementStatusCallback | None = None,
    ) -> SettlementResult:
        start = perf_counter()
        async with self._semaphore:
            lock = await self._session_lock(session_id)
            async with lock:
                if status_callback is not None:
                    await status_callback("running")
                return await self._settle_quarter_locked(session_id, start)

    async def _settle_quarter_locked(self, session_id: str, started_at: float) -> SettlementResult:
        ctx = await self.aggregator.build(session_id)
        logger.info(
            "settlement build complete",
            extra={"session_id": session_id, "quarter": ctx.quarter_number},
        )

        director_prompt = self.prompt_builder.build_director_prompt(ctx)
        director_resolution, llm_degraded, director_retries = await self._resolve_director(
            ctx,
            director_prompt,
        )

        press_bundle: PressBundle | None = None
        final_settlement = director_resolution.settlement
        llm_calls = 1
        llm_retries = director_retries

        if ctx.press_input is not None:
            press_prompt = self.prompt_builder.build_press_eval_prompt(ctx)
            press_resolution, press_degraded, press_retries = await self._resolve_press(
                ctx,
                press_prompt,
            )
            llm_degraded = llm_degraded or press_degraded
            llm_calls = 2
            llm_retries += press_retries
            combined_metrics_delta = director_resolution.settlement.metrics_delta.merge(
                press_resolution.extra_metrics_delta,
            )
            final_settlement = director_resolution.settlement.model_copy(
                update={"metrics_delta": combined_metrics_delta},
            )
            press_bundle = press_resolution.press_bundle

        session = await self.session_repo.get(session_id)
        if session is None:
            raise SessionNotFound(f"session not found: {session_id}")

        stats_before_settlement = session.stats
        preview_stats = stats_before_settlement.apply_delta(final_settlement.metrics_delta)
        scheduled_events = [
            event.model_copy(deep=True, update={"resolved": True})
            if event.fire_quarter == ctx.quarter_number and not event.resolved
            else event.model_copy(deep=True)
            for event in session.scheduled_events
        ]
        promise_log = _apply_promise_judgements(
            session.promise_log,
            director_resolution.promise_judgement,
            ctx.quarter_number,
        )
        agent_memory = session.agent_memory
        for entry in director_resolution.new_memory_entries:
            agent_memory = agent_memory.append(entry)

        quarter = session.quarter.model_copy(
            update={
                "settlement": final_settlement,
                "press_bundle": press_bundle,
            },
        )
        session = session.model_copy(
            update={
                "quarter": quarter,
                "scheduled_events": scheduled_events,
                "promise_log": promise_log,
                "agent_memory": agent_memory,
            },
        )
        await self.session_repo.save(session)

        session, finish_result = await self.state_machine.finish_settlement(
            session_id,
            final_settlement,
        )
        new_stats = session.stats
        history_added = session.history[-1] if session.history else HistoryEntry(
            quarter=ctx.quarter_number,
            decision_id=ctx.selected_decision.id,
            press_bundle_id=None,
            stats_before=stats_before_settlement,
            stats_after=preview_stats,
            settlement_summary=final_settlement.quarter_report[:60],
        )

        if press_bundle is not None:
            await self.press_archive_repo.append(session_id, press_bundle)

        for entry in director_resolution.new_memory_entries:
            await self.agent_memory_repo.append(session.player_id, session_id, entry)

        elapsed_ms = max(0, round((perf_counter() - started_at) * 1000))
        death_reason = finish_result.reason if finish_result.dead else None
        return SettlementResult(
            session_id=session.id,
            quarter_number=ctx.quarter_number,
            settlement=final_settlement,
            press_bundle=press_bundle,
            new_stats=new_stats,
            history_added=history_added,
            death_reason=death_reason,
            won=finish_result.won,
            llm_degraded=llm_degraded,
            latency_ms=elapsed_ms,
            llm_calls=llm_calls,
            llm_retries=llm_retries,
        )

    async def _resolve_director(
        self,
        ctx: Any,
        prompt: PromptBundle,
    ) -> tuple[DirectorResolution, bool, int]:
        log_context = {
            "session_id": ctx.session_id,
            "quarter": ctx.quarter_number,
            "prompt_kind": prompt.prompt_kind,
            "context_signature": prompt.context_signature,
        }
        degraded = False
        retry_count = 0
        try:
            response = await retry_chat_complete(
                self.llm_client,
                LLMRequest(
                    system=prompt.system,
                    user=prompt.user,
                    max_tokens=prompt.max_tokens,
                    temperature=prompt.temperature,
                    response_format_hint=prompt.response_format_hint,
                    timeout_ms=self.settings.llm_timeout_ms,
                ),
            )
            raw_text = response.raw_text
            retry_count = response.retry_count
        except LLMError as exc:
            self._record_failure("director_llm", exc)
            logger.warning(
                "director llm failed",
                extra={**log_context, "error_type": type(exc).__name__},
            )
            if not self._fallback_allowed():
                raise SettlementLLMCallError(prompt.prompt_kind, exc) from exc
            degraded = True
            raw_text = STUB_DIRECTOR
        except Exception as exc:
            self._record_failure("director_llm_unexpected", exc)
            logger.exception("director llm raised unexpected error", extra=log_context)
            if not self._fallback_allowed():
                raise SettlementLLMCallError(prompt.prompt_kind, exc) from exc
            degraded = True
            raw_text = STUB_DIRECTOR

        try:
            parsed = parse_director(raw_text, allow_repair=degraded)
        except ParseError as exc:
            self._record_failure("director_parse", exc)
            logger.warning("director parse failed", extra={**log_context, "error": repr(exc)})
            if not self._fallback_allowed():
                raise SettlementParseError(prompt.prompt_kind, exc) from exc
            degraded = True
            parsed = parse_director(STUB_DIRECTOR, allow_repair=True)
        try:
            return self.director_resolver.resolve(ctx, parsed), degraded, retry_count
        except Exception as exc:
            self._record_failure("director_resolve", exc)
            logger.warning("director resolution failed", extra={**log_context, "error": repr(exc)})
            if not self._fallback_allowed():
                raise SettlementResolveError(prompt.prompt_kind, exc) from exc
            degraded = True
            parsed = parse_director(STUB_DIRECTOR, allow_repair=True)
            return self.director_resolver.resolve(ctx, parsed), degraded, retry_count

    async def _resolve_press(
        self,
        ctx: Any,
        prompt: PromptBundle,
    ) -> tuple[PressResolution, bool, int]:
        log_context = {
            "session_id": ctx.session_id,
            "quarter": ctx.quarter_number,
            "prompt_kind": prompt.prompt_kind,
            "context_signature": prompt.context_signature,
        }
        degraded = False
        retry_count = 0
        try:
            response = await retry_chat_complete(
                self.llm_client,
                LLMRequest(
                    system=prompt.system,
                    user=prompt.user,
                    max_tokens=prompt.max_tokens,
                    temperature=prompt.temperature,
                    response_format_hint=prompt.response_format_hint,
                    timeout_ms=self.settings.llm_timeout_ms,
                ),
            )
            raw_text = response.raw_text
            retry_count = response.retry_count
        except LLMError as exc:
            self._record_failure("press_llm", exc)
            logger.warning(
                "press llm failed",
                extra={**log_context, "error_type": type(exc).__name__},
            )
            if not self._fallback_allowed():
                raise SettlementLLMCallError(prompt.prompt_kind, exc) from exc
            degraded = True
            raw_text = STUB_PRESS_EVAL
        except Exception as exc:
            self._record_failure("press_llm_unexpected", exc)
            logger.exception("press llm raised unexpected error", extra=log_context)
            if not self._fallback_allowed():
                raise SettlementLLMCallError(prompt.prompt_kind, exc) from exc
            degraded = True
            raw_text = STUB_PRESS_EVAL

        try:
            parsed = parse_press_eval(raw_text, allow_repair=degraded)
        except ParseError as exc:
            self._record_failure("press_parse", exc)
            logger.warning("press parse failed", extra={**log_context, "error": repr(exc)})
            if not self._fallback_allowed():
                raise SettlementParseError(prompt.prompt_kind, exc) from exc
            degraded = True
            parsed = parse_press_eval(STUB_PRESS_EVAL, allow_repair=True)
        try:
            return self.press_resolver.resolve(ctx, parsed), degraded, retry_count
        except Exception as exc:
            self._record_failure("press_resolve", exc)
            logger.warning("press resolution failed", extra={**log_context, "error": repr(exc)})
            if not self._fallback_allowed():
                raise SettlementResolveError(prompt.prompt_kind, exc) from exc
            degraded = True
            parsed = parse_press_eval(STUB_PRESS_EVAL, allow_repair=True)
            return self.press_resolver.resolve(ctx, parsed), degraded, retry_count

    async def _session_lock(self, session_id: str) -> asyncio.Lock:
        async with self._locks_guard:
            lock = self._locks.get(session_id)
            if lock is None:
                lock = asyncio.Lock()
                self._locks[session_id] = lock
            return lock

    def _record_failure(self, category: str, exc: Exception) -> None:
        self._failure_counts[category] += 1
        logger.debug("settlement failure counted", extra={"category": category, "error": repr(exc)})

    def _fallback_allowed(self) -> bool:
        return self.settings.env in {"dev", "test"} and self.settings.llm_allow_fallback


def _apply_promise_judgements(
    promises: list[Any],
    judgements: list[Any],
    judged_at_quarter: int,
) -> list[Any]:
    judgement_map: dict[str, tuple[bool, int]] = {}
    for item in judgements:
        if isinstance(item, tuple) and len(item) >= 2:
            judgement_map[str(item[0])] = (bool(item[1]), judged_at_quarter)
            continue
        promise_id = getattr(item, "promise_id", None)
        fulfilled = getattr(item, "fulfilled", None)
        item_quarter = getattr(item, "judged_at_quarter", judged_at_quarter)
        if promise_id is None or fulfilled is None:
            continue
        judgement_map[str(promise_id)] = (bool(fulfilled), int(item_quarter))

    updated = []
    for promise in promises:
        judgement = judgement_map.get(promise.id)
        if judgement is None:
            updated.append(promise.model_copy(deep=True))
            continue
        updated.append(
            promise.model_copy(
                update={
                    "fulfilled": judgement[0],
                    "judged_at_quarter": judgement[1],
                },
                deep=True,
            ),
        )
    return updated
