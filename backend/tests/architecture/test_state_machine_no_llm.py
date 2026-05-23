"""Architecture tests for the quarter state machine."""

from __future__ import annotations

import ast
import inspect

import app.services.quarter_state_machine as quarter_state_machine_module
from app.services.quarter_state_machine import QuarterStateMachine


def test_quarter_state_machine_source_has_no_generation_client_markers() -> None:
    source = inspect.getsource(quarter_state_machine_module)
    lowered = source.lower()

    assert "llm" not in lowered
    assert "chat_complete" not in lowered
    assert "openai" not in lowered
    assert "anthropic" not in lowered


def test_quarter_state_machine_imports_no_api_or_generation_modules() -> None:
    source = inspect.getsource(quarter_state_machine_module)
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

    assert QuarterStateMachine.__name__ == "QuarterStateMachine"
    assert not any(name.startswith("app.api") for name in imports if name is not None)
    assert not any(name.startswith("app.llm") for name in imports if name is not None)
