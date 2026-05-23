"""Public content registry exports."""

from .companies import (
    COMPANY_TEMPLATES,
    get_company_template_by_id,
    get_company_templates,
    sample_company_template,
)
from .decisions import (
    DECISION_CARDS,
    get_all_decision_cards,
    get_decision_card_by_id,
    sample_decision_cards,
)
from .employees import (
    EMPLOYEE_TEMPLATES,
    get_employee_template_by_id,
    get_employee_templates,
    sample_employee_set,
)
from .gossip_pool import (
    GOSSIP_TEMPLATES,
    get_gossip_templates_by_scene,
    sample_gossip_lead,
)
from .press_types import (
    PRESS_TYPES,
    get_default_press_for_quarter,
    get_press_type_by_id,
    list_press_types,
)


class ContentRegistryError(RuntimeError):
    """Raised when registry sampling or instantiation fails."""


__all__ = (
    "COMPANY_TEMPLATES",
    "DECISION_CARDS",
    "EMPLOYEE_TEMPLATES",
    "GOSSIP_TEMPLATES",
    "PRESS_TYPES",
    "ContentRegistryError",
    "get_all_decision_cards",
    "get_company_template_by_id",
    "get_company_templates",
    "get_decision_card_by_id",
    "get_default_press_for_quarter",
    "get_employee_template_by_id",
    "get_employee_templates",
    "get_gossip_templates_by_scene",
    "get_press_type_by_id",
    "list_press_types",
    "sample_company_template",
    "sample_decision_cards",
    "sample_employee_set",
    "sample_gossip_lead",
)
