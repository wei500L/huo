"""Architecture checks for settlement aggregation."""

from __future__ import annotations

import ast
import inspect

import app.services.settlement_aggregator as settlement_aggregator_module
from app.services.settlement_aggregator import SettlementInputAggregator


def test_settlement_aggregator_source_has_no_generation_markers() -> None:
    source = inspect.getsource(settlement_aggregator_module)
    lowered = source.lower()

    assert "llm" not in lowered
    assert "chat_complete" not in lowered


def test_settlement_aggregator_imports_only_domain_repo_content_modules() -> None:
    source = inspect.getsource(settlement_aggregator_module)
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

    assert SettlementInputAggregator.__name__ == "SettlementInputAggregator"
    assert not any(name.startswith("app.llm") for name in imports if name is not None)
    assert all(
        not name.startswith("app.") or name.startswith(("app.domain", "app.repo", "app.content"))
        for name in imports
        if name is not None
    )
