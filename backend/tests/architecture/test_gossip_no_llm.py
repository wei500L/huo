"""Architecture tests for gossip collection service."""

from __future__ import annotations

import ast
import inspect

import app.services.gossip_service as gossip_service_module
from app.services.gossip_service import GossipService


def test_gossip_service_source_has_no_generation_client_markers() -> None:
    source = inspect.getsource(gossip_service_module)
    lowered = source.lower()

    assert "llm" not in lowered
    assert "chat_complete" not in lowered


def test_gossip_service_imports_no_api_or_generation_modules() -> None:
    source = inspect.getsource(gossip_service_module)
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

    assert GossipService.__name__ == "GossipService"
    assert not any(name.startswith("app.api") for name in imports if name is not None)
    assert not any(name.startswith("app.llm") for name in imports if name is not None)
    assert not any(name.startswith("app.protocol") for name in imports if name is not None)
