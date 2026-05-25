"""Formatting helpers for settlement prompt construction."""

from __future__ import annotations

import re
from textwrap import indent

from app.domain import (
    DecisionCard,
    Employee,
    GossipLead,
    MemoryWindow,
    Promise,
    ScheduledEvent,
    Stats,
    StatsDelta,
)

_ROLE_PREFIXES = ("system:", "assistant:", "user:", "tool:", "developer:")
_COMMAND_PATTERNS = (
    re.compile(r"ignore previous instructions", re.IGNORECASE),
    re.compile(r"forget all", re.IGNORECASE),
    re.compile(r"override instructions", re.IGNORECASE),
    re.compile(r"disregard previous instructions", re.IGNORECASE),
)


def _format_stats(stats: Stats) -> str:
    return "\n".join(
        (
            f"- CASH: {stats.CASH}",
            f"- MORALE: {stats.MORALE}",
            f"- BOARD: {stats.BOARD}",
            f"- FACE: {stats.FACE}",
        )
    )


def _format_stats_trajectory(before: Stats, after: Stats) -> str:
    return "\n".join(
        (
            f"- before_immediate: CASH={before.CASH}, MORALE={before.MORALE}, "
            f"BOARD={before.BOARD}, FACE={before.FACE}",
            f"- after_immediate: CASH={after.CASH}, MORALE={after.MORALE}, "
            f"BOARD={after.BOARD}, FACE={after.FACE}",
        )
    )


def _format_company_brief(company_brief: dict[str, object]) -> str:
    if not company_brief:
        return "- none"
    lines: list[str] = []
    for key in ("name", "business", "founding_motto"):
        value = company_brief.get(key)
        if isinstance(value, str) and value.strip():
            lines.append(f"- {key}: {_escape_user_input(value)}")
    for key in ("deathCausesSummary", "hiddenRisks"):
        values = company_brief.get(key)
        if isinstance(values, list) and values:
            text = " / ".join(_escape_user_input(str(item)) for item in values[:4])
            lines.append(f"- {key}: {text}")
    return "\n".join(lines) if lines else "- none"


def _format_decision_card(card: DecisionCard) -> str:
    lines = [
        f"- id: {card.id}",
        f"- title: {_escape_user_input(card.title)}",
        f"- description: {_escape_user_input(card.description)}",
        f"- flavor: {_escape_user_input(card.flavor)}",
        f"- immediate_effect: {_format_stats_delta(card.immediate_effect)}",
    ]
    if card.long_term_hint is not None:
        lines.append(f"- long_term_hint: {_escape_user_input(card.long_term_hint)}")
    return "\n".join(lines)


def _format_gossip_leads(leads: list[GossipLead]) -> str:
    if not leads:
        return "- none"
    return "\n".join(
        "- "
        + " | ".join(
            (
                lead.id,
                f"q{lead.quarter}",
                lead.scene,
                lead.reliability.value,
                _escape_user_input(lead.text),
            )
        )
        for lead in leads[:6]
    )


def _format_employees(employees: list[Employee]) -> str:
    if not employees:
        return "- none"
    return "\n".join(
        "- "
        + " | ".join(
            (
                employee.id,
                _escape_user_input(employee.name),
                _escape_user_input(employee.role),
                f"loyalty={employee.loyalty}",
                f"stress={employee.stress}",
                f"mood={employee.mood.value}",
                f"goal={_escape_user_input(employee.current_goal or 'none')}",
            )
        )
        for employee in employees[:8]
    )


def _format_memory_window(window: MemoryWindow) -> str:
    if not window.entries:
        return "- none"
    return "\n".join(
        f"- q{entry.quarter} | {entry.actor.value} | {entry.event_type} | "
        f"{_escape_user_input(entry.summary)}"
        for entry in window.entries[: window.max_size]
    )


def _format_promises(promises: list[Promise]) -> str:
    if not promises:
        return "- none"
    return "\n".join(_format_promise(promise) for promise in promises)


def _format_scheduled_events(events: list[ScheduledEvent]) -> str:
    if not events:
        return "- none"
    return "\n".join(
        "- "
        + " | ".join(
            (
                event.id,
                f"fire_q{event.fire_quarter}",
                event.source_decision_id,
                _escape_user_input(event.description),
                _format_stats_delta(event.effect_on_fire),
            )
        )
        for event in events
    )


def _format_history(history: list[str]) -> str:
    if not history:
        return "- none"
    return "\n".join(f"- {_escape_user_input(item)}" for item in history)


def _quote_block(text: str) -> str:
    return indent(_escape_user_input(text), "    ")


def _escape_user_input(text: str) -> str:
    """Neutralize common prompt injection markers while preserving content."""

    escaped = "\n".join(_neutralize_line_prefix(line) for line in (text.splitlines() or [text]))
    if "```" in escaped or any(pattern.search(escaped) for pattern in _COMMAND_PATTERNS):
        return indent(escaped, "    ")
    return escaped


def _summarize_text(text: str, limit: int) -> str:
    collapsed = re.sub(r"\s+", " ", text).strip()
    if len(collapsed) <= limit:
        return collapsed
    return collapsed[: max(0, limit - 3)] + "..."


def _format_promise(promise: Promise) -> str:
    return "- " + " | ".join(
        (
            promise.id,
            f"q{promise.quarter_made}",
            promise.source.value,
            _escape_user_input(promise.text),
            _promise_status(promise),
            _format_promise_target(promise),
        )
    )


def _format_promise_target(promise: Promise) -> str:
    if promise.parsed is None:
        return "parsed:none"
    deadline = (
        f"q{promise.parsed.deadline_quarter}"
        if promise.parsed.deadline_quarter is not None
        else "none"
    )
    target = _escape_user_input(promise.parsed.target_expr)
    return f"parsed:{promise.parsed.metric}/{target}@{deadline}"


def _promise_status(promise: Promise) -> str:
    if promise.judged_at_quarter is None:
        return "status:pending"
    if promise.fulfilled is True:
        return f"status:fulfilled@q{promise.judged_at_quarter}"
    if promise.fulfilled is False:
        return f"status:broken@q{promise.judged_at_quarter}"
    return f"status:judged@q{promise.judged_at_quarter}"


def _format_stats_delta(delta: StatsDelta) -> str:
    values = delta.model_dump(exclude_none=True)
    if not values:
        return "{}"
    return "{" + ", ".join(f"{key}:{value}" for key, value in values.items()) + "}"


def _neutralize_line_prefix(line: str) -> str:
    stripped = line.lstrip()
    lowered = stripped.lower()
    if any(lowered.startswith(prefix) for prefix in _ROLE_PREFIXES):
        return f"  {stripped}"
    if stripped.startswith("#"):
        return f"  {stripped}"
    return line
