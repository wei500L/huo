"""Extra coverage for parser, normalizer, and rule-resolver branches."""

from __future__ import annotations

from types import SimpleNamespace

import pytest
from app.domain import PromiseTarget, Stats, StatsDelta
from app.llm._parser_defaults import (
    canonical_death_base,
    canonical_director_base,
    canonical_press_base,
)
from app.llm._parser_normalize import (
    apply_aliases,
    clamp_int_path,
    clamp_metrics_delta,
    compatible,
    filter_legacy_unlocks,
    get_path,
    literal_or_fallback,
    merge_shape,
    min_length_or_fallback,
    normalize_death_report,
    normalize_director,
    normalize_press_eval,
    normalize_scores,
    repair_keys,
    set_path,
    truncate_paths,
)
from app.llm.parser import (
    ParseError,
    ParseExtractionError,
    ParseSchemaError,
    extract_json_block,
    _extract_or_raise,
    _fallback_obj,
    _validate,
    parse_death_report,
    parse_director,
    parse_press_eval,
    parse_with_fallback,
)
from app.rules.director_resolver import DirectorResolver
from app.rules.press_resolver import PressResolver
from app.llm.schema import PressEvalRaw
from tests.factories import build_press_input, build_promise, build_scheduled_event

DIRECTOR_SCORES = {
    "contentCompleteness": 120,
    "issueResponse": 12,
    "overpromise": 18,
    "logicClarity": 61,
    "confidence": 55,
    "riskAvoidance": 49,
    "memorableQuote": 77,
    "weaknessExposed": 58,
    "authenticity": 63,
}


def test_parser_and_normalizer_heal_payloads() -> None:
    director_text = str(
        {
            "boardReaction": {
                "speech": "先把表格补齐，再谈下一步。",
                "patience_delta": 9,
                "vote": "maybe",
            },
            "employeeGossip": {
                "speaker": "小王",
                "line": "茶水间讨论太多",
                "mood": "sad",
            },
            "mediaHeadline": {
                "outlet": "36kr",
                "headline": "X" * 60,
                "tone": "bright",
            },
            "rivalAction": {
                "rival_name": "竞品",
                "action": "run",
                "move": "Y" * 100,
                "expected_damage": {
                    "CASH": 99,
                    "MORALE": True,
                    "BOARD": "bad",
                    "FACE": -99,
                },
            },
            "marketSignal": "zzz",
            "metricsDelta": {"CASH": 99, "MORALE": "bad", "BOARD": None, "FACE": -99},
            "quarterReport": "太短",
        }
    )
    press_text = str(
        {
            "scores": DIRECTOR_SCORES,
            "memorableQuote": "Q" * 90,
            "biggestFlaw": "F" * 200,
            "mediaAngle": "bad",
            "metricsDelta": {"CASH": 100, "MORALE": "x", "BOARD": False, "FACE": -999},
            "internalEval": "I" * 500,
        }
    )
    death_text = str(
        {
            "obituary": "too short",
            "biggestMistakeDecisionId": 123,
            "lastEmployee": "oops",
            "headlines": ["A"],
            "legacyUnlocks": ["PR_EXPERIENCE", "FACE_KEEPER"],
        }
    )

    assert extract_json_block("no json here") is None
    assert extract_json_block("{'a': 1}") == {"a": 1}
    assert parse_director(director_text).marketSignal == "bear"
    assert parse_press_eval(press_text).mediaAngle == "模糊带过"
    assert len(parse_death_report(death_text).headlines) == 3

    with pytest.raises(ParseExtractionError):
        parse_director("plain text")
    with pytest.raises(ParseSchemaError):
        _validate(PressEvalRaw, {})
    with pytest.raises(ParseSchemaError):
        _fallback_obj("plain text")
    with pytest.raises(ParseExtractionError):
        _extract_or_raise("plain text")

    seen: list[str] = []

    def parser(text: str) -> str:
        seen.append(text)
        if text == "raw":
            raise ParseExtractionError("boom")
        return f"ok:{text}"

    assert parse_with_fallback(parser, "raw", "fallback", {}) == "ok:fallback"
    assert seen == ["raw", "fallback"]

    def parser_with_bad_fallback(text: str) -> str:
        if text == "raw":
            raise ParseError("boom")
        raise RuntimeError("fallback broke")

    with pytest.raises(ParseError):
        parse_with_fallback(parser_with_bad_fallback, "raw", "fallback", {})

    director = normalize_director(
        {"boardReaction": {"speech": "x" * 100}},
        canonical_director_base(),
    )
    press = normalize_press_eval(
        {"scores": {"contentCompleteness": 999}},
        canonical_press_base(),
    )
    death = normalize_death_report(
        {"obituary": "x", "headlines": ["A"], "legacyUnlocks": ["PR_EXPERIENCE"]},
        canonical_death_base(),
    )

    assert director["boardReaction"]["vote"] == "abstain"
    assert press["scores"]["contentCompleteness"] == 100
    assert len(death["headlines"]) == 3

    repaired = repair_keys({"boardRection": {"speech": "ok"}}, {"boardReaction"})
    aliased = apply_aliases({"patience_delta": 1, "expected_damage": {"CASH": 1}})
    merged = merge_shape(
        {"a": {"b": 1}, "text": "keep"},
        {"a": {"b": 0, "c": 2}, "text": "fallback"},
    )

    assert "boardReaction" in repaired
    assert aliased["expectedDamage"]["CASH"] == 1
    assert compatible(1, 2) is True
    assert compatible("x", 1) is False
    assert get_path(merged, ("a", "b")) == 1

    set_path(merged, ("a", "d"), 3)
    clamp_int_path(merged, ("a", "d"), 0, 2)
    literal_or_fallback(merged, {"a": {"d": "fallback"}}, ("a", "d"), {"ok"})
    truncate_paths(merged, {("text",): 3})
    min_length_or_fallback(merged, {"text": "fallback"}, ("text",), 5)

    assert get_path(merged, ("a", "d")) == "fallback"
    assert merged["text"] == "fallback"
    assert clamp_metrics_delta({"CASH": 99, "MORALE": True, "BOARD": -99, "FACE": "x"}) == {
        "CASH": 10,
        "MORALE": 0,
        "BOARD": -15,
        "FACE": 0,
    }
    assert normalize_scores(
        {
            "contentCompleteness": 120,
            "issueResponse": -1,
            "overpromise": "x",
            "logicClarity": 61,
            "confidence": 55,
            "riskAvoidance": 49,
            "memorableQuote": 77,
            "weaknessExposed": 58,
            "authenticity": 63,
        }
    )["issueResponse"] == 0
    assert filter_legacy_unlocks(
        ["PR_EXPERIENCE", {"type": "FACE_KEEPER"}, "bogus"]
    ) == ["PR_EXPERIENCE"]


def test_rule_resolvers_cover_settlement_and_press_branches() -> None:
    director_resolver = DirectorResolver()
    press_resolver = PressResolver()

    director_ctx = SimpleNamespace(
        session_id="S-1",
        quarter_number=3,
        active_promises=[
            build_promise(parsed=None),
            build_promise(
                parsed=PromiseTarget(metric="CASH", target_expr="翻倍", deadline_quarter=3)
            ),
            build_promise(
                parsed=PromiseTarget(metric="CASH", target_expr=">= 60", deadline_quarter=3)
            ),
            build_promise(
                parsed=PromiseTarget(metric="CASH", target_expr="+50%", deadline_quarter=3)
            ),
            build_promise(
                parsed=PromiseTarget(metric="MORALE", target_expr="增长", deadline_quarter=3)
            ),
            build_promise(
                parsed=PromiseTarget(metric="SALES_HINT", target_expr="翻倍", deadline_quarter=3)
            ),
            build_promise(
                parsed=PromiseTarget(metric="CASH", target_expr="", deadline_quarter=3)
            ),
            build_promise(
                parsed=PromiseTarget(metric="CASH", target_expr="没戏", deadline_quarter=3)
            ),
            build_promise(
                parsed=PromiseTarget(metric="CASH", target_expr="翻倍", deadline_quarter=4)
            ),
        ],
        stats_after_immediate=Stats(CASH=65, MORALE=62, BOARD=50, FACE=55),
        scheduled_events_firing_this_quarter=[
            build_scheduled_event(fire_quarter=3),
            build_scheduled_event(
                fire_quarter=3,
                effect_on_fire=StatsDelta(MORALE=-2),
            ),
        ],
        meta_buff_signature="FACE_KEEPER/skip",
    )
    director_raw = SimpleNamespace(
        boardReaction=SimpleNamespace(
            speech="先把表格补齐，再谈下一步。",
            patienceDelta=9,
            vote="maybe",
        ),
        employeeGossip=SimpleNamespace(
            speaker="小王",
            line="茶水间讨论太多",
            mood="angry",
        ),
        mediaHeadline=SimpleNamespace(
            outlet="36kr",
            headline="X" * 60,
            tone="bright",
        ),
        rivalAction=SimpleNamespace(
            rival="竞品",
            action="run",
            move="Y" * 100,
            expectedDamage={
                "CASH": 99,
                "MORALE": True,
                "BOARD": "bad",
                "FACE": -99,
            },
        ),
        marketSignal="storm",
        metricsDelta={"CASH": 99, "MORALE": "bad", "BOARD": None, "FACE": -99},
        quarterReport="太短",
    )

    director_result = director_resolver.resolve(director_ctx, director_raw)

    assert len(director_result.promise_judgement) == 4
    assert len(director_result.new_memory_entries) == 3
    assert director_result.settlement.board_reaction.vote == "abstain"
    assert director_result.settlement.employee_gossip.mood == "angry"
    assert director_result.new_memory_entries[1].event_type == "betrayal"
    assert director_result.settlement.rival_action.action == "wait"
    assert director_result.settlement.market_signal == "neutral"
    assert len(director_result.settlement.quarter_report) >= 80

    low_cash = SimpleNamespace(
        press_input=build_press_input(seed=1),
        stats_after_immediate=Stats(CASH=10, MORALE=80, BOARD=80, FACE=80),
    )
    low_face = SimpleNamespace(
        press_input=build_press_input(seed=2),
        stats_after_immediate=Stats(CASH=80, MORALE=80, BOARD=80, FACE=10),
    )
    low_morale = SimpleNamespace(
        press_input=build_press_input(seed=3),
        stats_after_immediate=Stats(CASH=80, MORALE=10, BOARD=20, FACE=80),
    )
    press_raw = SimpleNamespace(
        scores=DIRECTOR_SCORES,
        memorableQuote="Q" * 90,
        biggestFlaw="F" * 200,
        mediaAngle="金句传播",
        metricsDelta={"CASH": 100, "MORALE": "x", "BOARD": False, "FACE": -999},
    )

    cash_result = press_resolver.resolve(low_cash, press_raw)
    face_raw = SimpleNamespace(**press_raw.__dict__)
    face_raw.mediaAngle = "漏洞放大"
    face_result = press_resolver.resolve(low_face, face_raw)
    morale_raw = SimpleNamespace(**press_raw.__dict__)
    morale_raw.mediaAngle = "bad"
    morale_result = press_resolver.resolve(low_morale, morale_raw)

    assert len(cash_result.press_bundle.headlines) == 2
    assert cash_result.press_bundle.headlines[0].headline.startswith("金句")
    assert len(face_result.press_bundle.headlines) == 2
    assert face_result.press_bundle.headlines[0].tone == "negative"
    assert len(morale_result.press_bundle.headlines) == 2
    assert morale_result.press_bundle.headlines[0].tone == "mocking"
    assert press_resolver.resolve(low_cash, press_raw).extra_metrics_delta.CASH == 15
