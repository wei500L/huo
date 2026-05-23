"""Architecture tests for decision-time services."""

from __future__ import annotations

import ast
import inspect

import app.services.decision_service as decision_service_module
import app.services.promise_extractor as promise_extractor_module
from app.services.decision_service import DecisionService


def test_decision_sources_have_no_generation_client_markers() -> None:
    for module in (decision_service_module, promise_extractor_module):
        lowered = inspect.getsource(module).lower()

        assert "llm" not in lowered
        assert "chat_complete" not in lowered


def test_decision_service_imports_no_api_or_generation_modules() -> None:
    source = inspect.getsource(decision_service_module)
    tree = ast.parse(source)
    imports = {
        alias.name
        for node in ast.walk(tree)
        if isinstance(node, ast.Import)
        for alias in node.names
    } | {
        node.module
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module is not None
    }

    assert DecisionService.__name__ == "DecisionService"
    assert not any(name.startswith("app.api") for name in imports if name is not None)
    assert not any(name.startswith("app.llm") for name in imports if name is not None)
