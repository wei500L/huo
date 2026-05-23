"""Public test factories."""

from __future__ import annotations

from ._factory_domain import (
    build_company,
    build_decision_card,
    build_employee,
    build_employees,
    build_stats,
)
from ._factory_runtime import (
    build_death_report_raw,
    build_director_raw,
    build_press_eval_raw,
    build_session,
    build_settlement_context,
)
from ._factory_story import (
    build_agent_memory,
    build_gossip_lead,
    build_legacy_unlock,
    build_meta_progress,
    build_press_evaluation,
    build_press_input,
    build_promise,
    build_quarter,
    build_scheduled_event,
    build_settlement,
)

__all__ = (
    "build_agent_memory",
    "build_company",
    "build_decision_card",
    "build_death_report_raw",
    "build_director_raw",
    "build_employee",
    "build_employees",
    "build_gossip_lead",
    "build_legacy_unlock",
    "build_meta_progress",
    "build_press_evaluation",
    "build_press_input",
    "build_press_eval_raw",
    "build_promise",
    "build_quarter",
    "build_scheduled_event",
    "build_session",
    "build_settlement",
    "build_settlement_context",
    "build_stats",
)
