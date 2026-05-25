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
    from .death_report_service import (
        DeathReportLLMError,
        DeathReportParseError,
        DeathReportService,
        DeathReportServiceError,
        InvalidTerminalSession,
    )
    from .legacy_resolver import LegacyEvaluation, LegacyResolver
    from .settlement_orchestrator import (
        SettlementError,
        SettlementLLMCallError,
        SettlementOrchestrator,
        SettlementParseError,
        SettlementResolveError,
        SettlementResult,
    )

__all__ = (
    "CardNotInDraw",
    "CompanyService",
    "DeathReportLLMError",
    "DeathReportParseError",
    "DeathReportService",
    "DeathReportServiceError",
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
    "InvalidTerminalSession",
    "LegacyEvaluation",
    "LegacyResolver",
    "PressInputService",
    "PressInputServiceError",
    "NoDecisionSelected",
    "NotInSettlementPhase",
    "SettlementAggregatorError",
    "SettlementContext",
    "SettlementInputAggregator",
    "SettlementError",
    "SettlementLLMCallError",
    "SettlementOrchestrator",
    "SettlementParseError",
    "SettlementResolveError",
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
    if name in {
        "DeathReportService",
        "DeathReportServiceError",
        "DeathReportLLMError",
        "DeathReportParseError",
        "InvalidTerminalSession",
        "LegacyEvaluation",
        "LegacyResolver",
        "SettlementError",
        "SettlementLLMCallError",
        "SettlementOrchestrator",
        "SettlementParseError",
        "SettlementResolveError",
        "SettlementResult",
    }:
        module_name = {
            "DeathReportService": ".death_report_service",
            "DeathReportServiceError": ".death_report_service",
            "DeathReportLLMError": ".death_report_service",
            "DeathReportParseError": ".death_report_service",
            "InvalidTerminalSession": ".death_report_service",
            "LegacyEvaluation": ".legacy_resolver",
            "LegacyResolver": ".legacy_resolver",
            "SettlementError": ".settlement_orchestrator",
            "SettlementLLMCallError": ".settlement_orchestrator",
            "SettlementOrchestrator": ".settlement_orchestrator",
            "SettlementParseError": ".settlement_orchestrator",
            "SettlementResolveError": ".settlement_orchestrator",
            "SettlementResult": ".settlement_orchestrator",
        }[name]
        module = import_module(module_name, __name__)
        value = getattr(module, name)
        globals()[name] = value
        return value
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
