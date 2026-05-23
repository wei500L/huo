"""Architecture guardrail for backend layer dependencies."""

from __future__ import annotations

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] / "app"

FORBIDDEN_BY_LAYER: dict[str, set[str]] = {
    "domain": {"services", "api", "llm", "protocol", "rules", "repo"},
    "protocol": {"services", "api", "llm", "rules"},
    "content": {"services", "api", "llm", "rules"},
    "repo": {"services", "api", "llm", "rules"},
    "llm": {"services", "api", "rules"},
    "rules": {"services", "api", "llm", "protocol", "repo"},
}


def test_layer_imports_only_allowed_directions() -> None:
    violations: list[str] = []
    for layer, forbidden_layers in FORBIDDEN_BY_LAYER.items():
        for path in sorted((ROOT / layer).glob("*.py")):
            if path.name == "__init__.py":
                continue
            imported_layers = _imported_app_layers(path)
            for imported_layer, imported_module, lineno in imported_layers:
                if imported_layer in forbidden_layers:
                    violations.append(
                        f"{path}:{lineno} {layer} imports forbidden {imported_module}"
                    )

    assert not violations, "\n".join(violations)


def test_settlement_orchestrator_does_not_bypass_llm_client() -> None:
    path = ROOT / "services" / "settlement_orchestrator.py"
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    forbidden_names = {"OpenAICompatibleClient", "MockLLMClient", "get_llm_client"}
    violations: list[str] = []
    imported_names: set[str] = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            for alias in node.names:
                imported_names.add(alias.asname or alias.name)
                if alias.name in forbidden_names:
                    violations.append(f"{path}:{node.lineno} imports {alias.name}")
        elif isinstance(node, ast.Import):
            for alias in node.names:
                name = alias.asname or alias.name
                imported_names.add(name)
                if alias.name.endswith(".client") or alias.name in forbidden_names:
                    violations.append(f"{path}:{node.lineno} imports {alias.name}")
        elif isinstance(node, ast.Call):
            call_name = _call_name(node.func)
            if call_name in forbidden_names:
                violations.append(f"{path}:{node.lineno} calls {call_name}")

    assert "LLMClient" in imported_names
    assert not violations, "\n".join(violations)


def _imported_app_layers(path: Path) -> list[tuple[str, str, int]]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    found: list[tuple[str, str, int]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                layer = _app_layer(alias.name)
                if layer is not None:
                    found.append((layer, alias.name, node.lineno))
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module is not None:
            layer = _app_layer(node.module)
            if layer is not None:
                found.append((layer, node.module, node.lineno))
    return found


def _app_layer(module_name: str) -> str | None:
    parts = module_name.split(".")
    if len(parts) < 2 or parts[0] != "app":
        return None
    return parts[1]


def _call_name(node: ast.expr) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return node.attr
    return ""
