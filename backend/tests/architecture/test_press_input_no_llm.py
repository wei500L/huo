"""Architecture checks for press input intake."""

from __future__ import annotations

import ast
import inspect

import app.safety.brand_blacklist as brand_blacklist_module
import app.safety.transcript_cleaner as transcript_cleaner_module
import app.services.press_input_service as press_input_service_module
from app.services.press_input_service import PressInputService


def test_press_input_sources_have_no_generation_markers() -> None:
    for module in (
        brand_blacklist_module,
        transcript_cleaner_module,
        press_input_service_module,
    ):
        source = inspect.getsource(module)
        lowered = source.lower()

        assert "llm" not in lowered
        assert "chat_complete" not in lowered


def test_press_input_service_imports_no_generation_modules() -> None:
    source = inspect.getsource(press_input_service_module)
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

    assert PressInputService.__name__ == "PressInputService"
    assert not any(name.startswith("app.llm") for name in imports if name is not None)
