"""Death report generation and end-of-run meta persistence."""

from __future__ import annotations

import hashlib
import logging
from datetime import UTC, datetime
from typing import cast

from app.config import Settings, get_settings
from app.content.decisions import get_decision_card_by_id
from app.domain import (
    DeathLogEntry,
    DeathReason,
    DecisionCard,
    DecisionCategory,
    Employee,
    HistoryEntry,
    MemoryWindow,
    ScheduledEvent,
    Stats,
    StatsDelta,
)
from app.llm._client_types import LLMClient, LLMError, LLMRequest
from app.llm.client import retry_chat_complete
from app.llm.fallback import STUB_DEATH_REPORT
from app.llm.parser import ParseError, parse_death_report
from app.llm.prompt_builder import PromptBuilder
from app.protocol.outbound import DeathReportBundle
from app.repo.protocols import GameSession, GameSessionRepo, MetaProgressRepo, PressArchiveRepo
from app.services.legacy_resolver import LegacyResolver
from app.services.settlement_aggregator import SessionNotFound, SettlementContext

logger = logging.getLogger(__name__)

__all__ = (
    "DeathReportLLMError",
    "DeathReportParseError",
    "DeathReportService",
    "DeathReportServiceError",
    "InvalidTerminalSession",
)

_FORBIDDEN_OBITUARY_MARKERS = ("internal_eval", "internalEval", "hidden_secrets")
_FALLBACK_HEADLINES = ("止血动作来得太晚", "组织信心持续下滑", "市场开始重新定价")


class DeathReportServiceError(Exception):
    pass


class InvalidTerminalSession(DeathReportServiceError):
    pass


class DeathReportLLMError(DeathReportServiceError):
    pass


class DeathReportParseError(DeathReportServiceError):
    pass


class _WonPromptReason:
    title = "撑过 Q4"
    value = "WON"


class DeathReportService:
    """Generate an obituary, resolve unlocks, and persist meta progress."""

    def __init__(
        self,
        session_repo: GameSessionRepo,
        meta_repo: MetaProgressRepo,
        press_archive_repo: PressArchiveRepo,
        prompt_builder: PromptBuilder,
        llm_client: LLMClient,
        legacy_resolver: LegacyResolver,
        settings: Settings | None = None,
    ) -> None:
        self.session_repo = session_repo
        self.meta_repo = meta_repo
        self.press_archive_repo = press_archive_repo
        self.prompt_builder = prompt_builder
        self.llm_client = llm_client
        self.legacy_resolver = legacy_resolver
        self.settings = settings or get_settings()

    async def generate(
        self,
        session_id: str,
        death_reason: DeathReason | None = None,
    ) -> DeathReportBundle:
        session = await self.session_repo.get(session_id)
        if session is None:
            raise SessionNotFound(f"session not found: {session_id}")
        if session.status not in {"dead", "won"}:
            raise InvalidTerminalSession(f"session {session_id} is not terminal: {session.status}")
        if death_reason is None and session.status == "dead":
            death_reason = session.stats.is_dead()

        ctx = _build_death_context(session)
        prompt_reason = _prompt_reason(death_reason)
        prompt = self.prompt_builder.build_death_report_prompt(
            ctx,
            cast(DeathReason, prompt_reason),
        )
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
            logger.warning(
                "death report llm failed",
                extra={
                    "session_id": session_id,
                    "prompt_kind": prompt.prompt_kind,
                    "context_signature": prompt.context_signature,
                    "error_type": type(exc).__name__,
                },
            )
            if not self._fallback_allowed():
                raise DeathReportLLMError(f"death_report LLM call failed: {exc}") from exc
            degraded = True
            raw_text = STUB_DEATH_REPORT
        except Exception as exc:
            logger.exception(
                "death report llm raised unexpected error",
                extra={"session_id": session_id, "prompt_kind": prompt.prompt_kind},
            )
            if not self._fallback_allowed():
                raise DeathReportLLMError(f"death_report LLM call failed: {exc}") from exc
            degraded = True
            raw_text = STUB_DEATH_REPORT

        try:
            parsed = parse_death_report(raw_text, allow_repair=degraded)
        except ParseError as exc:
            logger.warning(
                "death report parse failed",
                extra={"session_id": session_id, "prompt_kind": "death_report", "error": repr(exc)},
            )
            if not self._fallback_allowed():
                raise DeathReportParseError(f"death_report parse failed: {exc}") from exc
            degraded = True
            parsed = parse_death_report(STUB_DEATH_REPORT, allow_repair=True)
        obituary = _clean_obituary(parsed.obituary)
        headlines = _normalize_headlines(parsed.headlines)
        last_employee = parsed.lastEmployee if isinstance(parsed.lastEmployee, dict) else None
        text = _optional_text
        last_employee_name = text(last_employee, "name")
        last_employee_quote = text(last_employee, "quote") or text(last_employee, "line")

        press_archive = await self.press_archive_repo.list_by_session(session_id)
        meta_before = await self.meta_repo.get(session.player_id)
        evaluation = self.legacy_resolver.evaluate(
            session.history,
            press_archive,
            meta_before,
            died_at_quarter=session.quarter.number,
            death_reason=death_reason,
            run_id=session_id,
            employees_snapshot=session.employees,
            promise_log=session.promise_log,
        )
        death_log_entry = DeathLogEntry(
            run_id=session_id,
            company_name=session.company.name,
            business=session.company.business,
            died_at_quarter=session.quarter.number,
            death_reason=death_reason,
            obituary=obituary,
            biggest_mistake_decision_id=parsed.biggestMistakeDecisionId,
            last_employee_quote=last_employee_quote,
            headlines=headlines,
        )
        meta = await self.meta_repo.get(session.player_id)
        new_legacies = evaluation.new_legacies
        new_styles = evaluation.new_styles
        meta = meta.register_run_end(death_log_entry, new_legacies, new_styles)
        await self.meta_repo.save(meta)

        return DeathReportBundle.from_domain(
            session_id=session_id,
            death_log_entry=death_log_entry,
            legacy_unlocks=evaluation.new_legacies,
            styles_unlocked=evaluation.new_styles,
            last_employee_name=last_employee_name,
            last_employee_quote=last_employee_quote,
            llm_degraded=degraded,
            llm_retry_count=retry_count,
        )

    def _fallback_allowed(self) -> bool:
        return self.settings.env in {"dev", "test"} and self.settings.llm_allow_fallback


def _prompt_reason(death_reason: DeathReason | None) -> object:
    return death_reason if death_reason is not None else _WonPromptReason()


def _build_death_context(session: GameSession) -> SettlementContext:
    selected_decision = _selected_decision(session)
    stats_before = _stats_before_terminal(session.history, session.stats)
    immediate_effect = _stats_delta(stats_before, session.stats)
    return SettlementContext(
        session_id=session.id,
        player_id=session.player_id,
        quarter_number=session.quarter.number,
        company_brief=_company_brief(session),
        stats_before_immediate=stats_before,
        stats_after_immediate=session.stats,
        selected_decision=selected_decision,
        immediate_effect_applied=immediate_effect,
        gossip_collected=[lead.model_copy(deep=True) for lead in session.quarter.collected_leads],
        press_input=session.quarter.press_input.model_copy(deep=True)
        if session.quarter.press_input is not None
        else None,
        press_type=session.quarter.press_input.press_type
        if session.quarter.press_input is not None
        else None,
        press_must_answer=list(session.quarter.press_input.must_answer_topics)
        if session.quarter.press_input is not None
        else [],
        active_promises=[promise.model_copy(deep=True) for promise in session.promise_log],
        agent_memory_window=_memory_window(session.agent_memory),
        scheduled_events_firing_this_quarter=_scheduled_events(session),
        history_summary=[entry.settlement_summary for entry in session.history],
        employees_snapshot=[_sanitize_employee(employee) for employee in session.employees],
        meta_buff_signature="",
        rng_seed_for_aggregation=_rng_seed(session),
        aggregated_at=datetime.now(UTC),
    )


def _selected_decision(session: GameSession) -> DecisionCard:
    selected_id = session.quarter.selected_decision_id
    for card in session.quarter.decision_cards:
        if card.id == selected_id:
            return card.model_copy(deep=True)
    fallback_id = selected_id or (session.history[-1].decision_id if session.history else "")
    card_data: dict[str, object] | None = get_decision_card_by_id(fallback_id)
    if card_data is not None:
        return DecisionCard.model_validate(card_data)
    return _placeholder_decision(fallback_id or "D_UNKNOWN", session.history, session.stats)


def _placeholder_decision(
    decision_id: str,
    history: list[HistoryEntry],
    current_stats: Stats,
) -> DecisionCard:
    stats_before = _stats_before_terminal(history, current_stats)
    return DecisionCard(
        id=decision_id,
        category=_category_from_id(decision_id),
        title="终局复盘",
        description="终局阶段缺少原始决策卡",
        immediate_effect=_stats_delta(stats_before, current_stats),
        flavor="复盘只保留可验证事实",
        long_term_hint=None,
        boomerang_seeds=[],
    )


def _category_from_id(decision_id: str) -> DecisionCategory:
    normalized = decision_id.upper().replace("-", "_")
    for category in DecisionCategory:
        if category.value in normalized:
            return category
    return DecisionCategory.HIDE_BAD_NEWS


def _stats_before_terminal(history: list[HistoryEntry], current_stats: Stats) -> Stats:
    return history[-1].stats_before if history else current_stats


def _stats_delta(before: Stats, after: Stats) -> StatsDelta:
    return StatsDelta(
        CASH=after.CASH - before.CASH,
        MORALE=after.MORALE - before.MORALE,
        BOARD=after.BOARD - before.BOARD,
        FACE=after.FACE - before.FACE,
    )


def _company_brief(session: GameSession) -> dict[str, object]:
    return {
        "name": session.company.name,
        "business": session.company.business,
        "founding_motto": session.company.founding_motto,
        "deathCausesSummary": [cause.description for cause in session.company.death_causes],
        "hiddenRisks": [],
    }


def _memory_window(window: MemoryWindow) -> MemoryWindow:
    return window.model_copy(deep=True, update={"entries": window.entries[: window.max_size]})


def _scheduled_events(session: GameSession) -> list[ScheduledEvent]:
    return [event.model_copy(deep=True) for event in session.scheduled_events]


def _sanitize_employee(employee: Employee) -> Employee:
    return employee.model_copy(deep=True, update={"hidden_secrets": []})


def _rng_seed(session: GameSession) -> int:
    payload = f"{session.id}|{session.player_id}|death_report|{session.quarter.number}"
    return int.from_bytes(hashlib.sha256(payload.encode("utf-8")).digest()[:8], "big")


def _clean_obituary(obituary: str) -> str:
    cleaned = obituary.strip()
    for marker in _FORBIDDEN_OBITUARY_MARKERS:
        cleaned = cleaned.replace(marker, "[redacted]")
    if len(cleaned) > 500:
        cleaned = cleaned[:500]
    if len(cleaned) < 200:
        fallback = parse_death_report(STUB_DEATH_REPORT, allow_repair=True).obituary
        return fallback[:500]
    return cleaned


def _normalize_headlines(headlines: list[str]) -> list[str]:
    cleaned = [item.strip()[:80] for item in headlines if item.strip()]
    cleaned = cleaned[:3]
    cleaned.extend(_FALLBACK_HEADLINES[len(cleaned) : 3])
    return cleaned


def _optional_text(data: dict[str, object] | None, key: str) -> str | None:
    if data is None:
        return None
    value = data.get(key)
    if isinstance(value, str) and value.strip():
        return value.strip()
    return None
