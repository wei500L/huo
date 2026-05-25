"""Architecture guardrail: realtime services never call LLMs."""

from __future__ import annotations

import ast
from collections.abc import Awaitable
from pathlib import Path
from typing import TypeVar
from uuid import uuid4

import pytest

from app.domain import DecisionCategory, PressType, QuarterPhase, StatsDelta
from tests.factories import (
    build_decision_card,
    build_director_raw,
    build_press_eval_raw,
    build_stats,
)
from tests.llm_spy import SpyLLMClient, raw_json

T = TypeVar("T")

ROOT = Path(__file__).resolve().parents[2]
SERVICES_DIR = ROOT / "app" / "services"
REALTIME_SERVICES = {
    "company_service.py",
    "quarter_state_machine.py",
    "decision_service.py",
    "gossip_service.py",
    "press_input_service.py",
    "promise_extractor.py",
}
FORBIDDEN_STRINGS = {"chat_complete", "openai", "anthropic"}


def test_realtime_services_import_no_llm_modules_or_markers() -> None:
    service_files = {path.name: path for path in SERVICES_DIR.glob("*.py")}
    assert REALTIME_SERVICES.issubset(service_files)

    violations: list[str] = []
    for filename in sorted(REALTIME_SERVICES):
        path = service_files[filename]
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for module_name, lineno in _imports(tree):
            if module_name == "app.llm" or module_name.startswith("app.llm."):
                violations.append(f"{path}:{lineno} imports {module_name}")
        for literal, lineno in _string_literals(tree):
            lowered = literal.lower()
            for token in FORBIDDEN_STRINGS:
                if token in lowered:
                    violations.append(f"{path}:{lineno} contains string literal {token!r}")

    assert not violations, "\n".join(violations)


@pytest.mark.asyncio
async def test_realtime_operations_make_zero_llm_calls_until_settlement(
    full_stack: tuple[object, ...],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "app.services.decision_service.sample_decision_cards",
        _safe_decision_cards,
    )
    (
        company_service,
        decision_service,
        gossip_service,
        press_input_service,
        orchestrator,
        death_report_service,
        state_machine,
    ) = full_stack
    spy = SpyLLMClient(
        {
            "director": raw_json(build_director_raw(seed=1)),
            "press_eval": raw_json(build_press_eval_raw(seed=1)),
        }
    )
    orchestrator.llm_client = spy
    death_report_service.llm_client = spy

    session = await _assert_no_new_llm(
        company_service.create_new_run(player_id=str(uuid4()), rng_seed=91),
        spy,
    )
    session = session.model_copy(
        update={"stats": build_stats(CASH=95, MORALE=95, BOARD=95, FACE=95)}
    )
    await company_service.session_repo.save(session)

    final_result = None
    for quarter in range(1, 5):
        await _assert_no_new_llm(
            state_machine.transition_to(session.id, QuarterPhase.GOSSIP),
            spy,
        )
        await _assert_no_new_llm(
            gossip_service.collect_gossip(session.id, "tearoom", rng_seed=quarter),
            spy,
        )
        await _assert_no_new_llm(
            state_machine.transition_to(session.id, QuarterPhase.DECISION),
            spy,
        )
        drawn = await _assert_no_new_llm(
            decision_service.draw_decision_cards(session.id, rng_seed=quarter),
            spy,
        )
        selected = drawn.quarter.decision_cards[0]
        await _assert_no_new_llm(
            decision_service.select_decision(session.id, selected.id, rng_seed=quarter),
            spy,
        )

        if quarter == 3:
            await _assert_no_new_llm(
                press_input_service.submit(
                    session.id,
                    PressType.CRISIS,
                    "我们会持续回应市场关切，并明确现金流、组织调整和产品节奏的后续动作。",
                    duration_s=90,
                ),
                spy,
            )

        before_settlement = len(spy.calls)
        final_result = await orchestrator.settle_quarter(session.id)
        expected_calls = 2 if quarter == 3 else 1
        assert len(spy.calls) - before_settlement == expected_calls

    assert final_result is not None
    assert final_result.won is True
    assert spy.call_kinds == ["director", "director", "director", "press_eval", "director"]
    assert 5 <= len(spy.calls) <= 6


async def _assert_no_new_llm(awaitable: Awaitable[T], spy: SpyLLMClient) -> T:
    before = len(spy.calls)
    result = await awaitable
    assert len(spy.calls) == before
    return result


def _safe_decision_cards(
    n: int,
    quarter: int,
    current_stats: object | None = None,
    rng_seed: int | None = None,
) -> list[dict[str, object]]:
    cards = [
        build_decision_card(
            id=f"D_SAFE_Q{quarter}",
            category=DecisionCategory.SOOTHE,
            title="稳住团队",
            description="给团队一点修复时间",
            immediate_effect=StatsDelta(CASH=0, MORALE=4, BOARD=1, FACE=1),
            flavor="话术不值钱，真心值",
            long_term_hint=None,
            boomerang_seeds=[],
        ),
        build_decision_card(
            id=f"D_BOARD_Q{quarter}",
            category=DecisionCategory.DELAY_BOARD,
            title="稳住董事",
            description="争取一季缓冲期",
            immediate_effect=StatsDelta(CASH=0, MORALE=1, BOARD=3, FACE=0),
            flavor="耐心是借来的",
            long_term_hint=None,
            boomerang_seeds=[],
        ),
        build_decision_card(
            id=f"D_FACE_Q{quarter}",
            category=DecisionCategory.NEGOTIATE_RIVAL,
            title="谈个缓冲",
            description="试着把竞争变成合作",
            immediate_effect=StatsDelta(CASH=1, MORALE=1, BOARD=1, FACE=2),
            flavor="桌上谈判，桌下拔刀",
            long_term_hint=None,
            boomerang_seeds=[],
        ),
    ]
    return [card.model_dump(mode="json") for card in cards[:n]]


def _imports(tree: ast.AST) -> list[tuple[str, int]]:
    found: list[tuple[str, int]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            found.extend((alias.name, node.lineno) for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module is not None:
            found.append((node.module, node.lineno))
    return found


def _string_literals(tree: ast.AST) -> list[tuple[str, int]]:
    return [
        (node.value, node.lineno)
        for node in ast.walk(tree)
        if isinstance(node, ast.Constant) and isinstance(node.value, str)
    ]
