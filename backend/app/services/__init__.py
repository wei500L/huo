"""Services package exports."""

from importlib import import_module
from typing import TYPE_CHECKING

from .company_service import CompanyService
from .decision_service import (
    CardNotInDraw,
    DecisionNotFound,
    DecisionResult,
    DecisionService,
    DecisionServiceError,
    InvalidPhaseForDecision,
)
from .gossip_service import (
    GossipService,
    GossipServiceError,
    InsufficientAP,
    InvalidPhaseForGossip,
    InvalidScene,
)
from .press_input_service import (
    InvalidPressPhase,
    PressInputService,
    PressInputServiceError,
    SubmitPressResult,
    TranscriptRejected,
    WrongPressQuarter,
)
from .quarter_state_machine import (
    FinishResult,
    IllegalTransitionError,
    QuarterStateMachine,
    StateMachineError,
    WrongQuarterError,
)
from .settlement_aggregator import (
    NoDecisionSelected,
    NotInSettlementPhase,
    SessionNotFound,
    SettlementAggregatorError,
    SettlementContext,
    SettlementInputAggregator,
)

if TYPE_CHECKING:
    from .settlement_orchestrator import SettlementOrchestrator, SettlementResult

__all__ = (
    "CardNotInDraw",
    "CompanyService",
    "DecisionNotFound",
    "DecisionResult",
    "DecisionService",
    "DecisionServiceError",
    "GossipService",
    "GossipServiceError",
    "FinishResult",
    "InsufficientAP",
    "IllegalTransitionError",
    "InvalidPhaseForDecision",
    "InvalidPhaseForGossip",
    "InvalidScene",
    "InvalidPressPhase",
    "PressInputService",
    "PressInputServiceError",
    "NoDecisionSelected",
    "NotInSettlementPhase",
    "SettlementAggregatorError",
    "SettlementContext",
    "SettlementInputAggregator",
    "SettlementOrchestrator",
    "SettlementResult",
    "QuarterStateMachine",
    "StateMachineError",
    "SubmitPressResult",
    "SessionNotFound",
    "TranscriptRejected",
    "WrongQuarterError",
    "WrongPressQuarter",
)


def __getattr__(name: str) -> object:
    if name in {"SettlementOrchestrator", "SettlementResult"}:
        module = import_module(".settlement_orchestrator", __name__)
        value = getattr(module, name)
        globals()[name] = value
        return value
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
