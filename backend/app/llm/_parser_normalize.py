from __future__ import annotations

from collections.abc import Mapping
from copy import deepcopy
from difflib import get_close_matches
from typing import Any

from app.domain import LegacyType

from ._parser_defaults import canonical_death_base, canonical_director_base, canonical_press_base
from .schema import METRIC_KEYS, SCORE_KEYS

DIRECTOR_KEYS = {
    "boardReaction",
    "speech",
    "patienceDelta",
    "vote",
    "employeeGossip",
    "speaker",
    "line",
    "mood",
    "mediaHeadline",
    "outlet",
    "headline",
    "tone",
    "rivalAction",
    "rival",
    "action",
    "move",
    "expectedDamage",
    "marketSignal",
    "metricsDelta",
    "quarterReport",
}
PRESS_KEYS = {
    "scores",
    "memorableQuote",
    "biggestFlaw",
    "mediaAngle",
    "metricsDelta",
    "internalEval",
    *SCORE_KEYS,
}
DEATH_KEYS = {"obituary", "biggestMistakeDecisionId", "lastEmployee", "headlines", "legacyUnlocks"}
FIELD_ALIASES = {
    "patience_delta": "patienceDelta",
    "rival_name": "rival",
    "description": "move",
    "expected_damage": "expectedDamage",
    "biggest_mistake_decision_id": "biggestMistakeDecisionId",
    "last_employee": "lastEmployee",
    "legacy_unlocks": "legacyUnlocks",
}
SCORE_ALIASES = {
    "memorableQuote": "quotability",
    "memorable_quote": "quotability",
}
DIRECTOR_LIMITS: Mapping[tuple[str, ...], int] = {
    ("boardReaction", "speech"): 80,
    ("employeeGossip", "speaker"): 12,
    ("employeeGossip", "line"): 50,
    ("mediaHeadline", "headline"): 22,
    ("rivalAction", "rival"): 20,
    ("rivalAction", "move"): 60,
    ("quarterReport",): 200,
}
PRESS_LIMITS: Mapping[tuple[str, ...], int] = {
    ("memorableQuote",): 80, ("biggestFlaw",): 120, ("internalEval",): 200,
}


def clamp_metrics_delta(d: dict[Any, Any], range_: tuple[int, int] = (-15, 10)) -> dict[str, int]:
    low, high = range_
    clamped: dict[str, int] = {}
    for key in METRIC_KEYS:
        raw_value = d.get(key, 0)
        value = raw_value if isinstance(raw_value, int) and not isinstance(raw_value, bool) else 0
        clamped[key] = min(high, max(low, value))
    return clamped


def normalize_director(obj: dict[str, Any], fallback: dict[str, Any]) -> dict[str, Any]:
    source = apply_aliases(repair_keys(obj, DIRECTOR_KEYS))
    fallback = normalize_director_fallback(fallback)
    result = merge_shape(source, fallback)
    result["metricsDelta"] = clamp_metrics_delta(as_dict(result.get("metricsDelta")))
    rival = as_dict(result.get("rivalAction"))
    rival["expectedDamage"] = clamp_metrics_delta(as_dict(rival.get("expectedDamage")))
    result["rivalAction"] = rival
    clamp_int_path(result, ("boardReaction", "patienceDelta"), -2, 1)
    literal_or_fallback(
        result, fallback, ("boardReaction", "vote"), {"approve", "oppose", "abstain"},
    )
    literal_or_fallback(
        result,
        fallback,
        ("employeeGossip", "mood"),
        {"anxious", "angry", "tired", "hopeful", "numb", "excited", "in_love", "neutral"},
    )
    literal_or_fallback(
        result,
        fallback,
        ("mediaHeadline", "tone"),
        {"positive", "neutral", "negative", "mocking"},
    )
    literal_or_fallback(
        result,
        fallback,
        ("rivalAction", "action"),
        {"price_war", "poach", "launch", "pr_attack", "wait", "acquisition_rumor"},
    )
    literal_or_fallback(result, fallback, ("marketSignal",), {"bull", "neutral", "bear", "crisis"})
    truncate_paths(result, DIRECTOR_LIMITS)
    min_length_or_fallback(result, fallback, ("quarterReport",), 40)
    return result


def normalize_press_eval(obj: dict[str, Any], fallback: dict[str, Any]) -> dict[str, Any]:
    source = repair_keys(obj, PRESS_KEYS)
    source_scores = as_dict(source.get("scores"))
    fallback = merge_shape(repair_keys(fallback, PRESS_KEYS), canonical_press_base())
    result = merge_shape(source, fallback)
    result["metricsDelta"] = clamp_metrics_delta(as_dict(result.get("metricsDelta")))
    result["scores"] = normalize_scores(source_scores)
    if result.get("mediaAngle") not in {"金句传播", "漏洞放大", "模糊带过"}:
        result["mediaAngle"] = "模糊带过"
    truncate_paths(result, PRESS_LIMITS)
    return result


def normalize_death_report(obj: dict[str, Any], fallback: dict[str, Any]) -> dict[str, Any]:
    source = apply_aliases(repair_keys(obj, DEATH_KEYS))
    fallback = normalize_death_fallback(fallback)
    result = merge_shape(source, fallback)
    headlines = result.get("headlines")
    fallback_headlines = fallback["headlines"]
    if not isinstance(headlines, list):
        result["headlines"] = fallback_headlines
    else:
        result["headlines"] = [str(item)[:80] for item in headlines[:3]]
        result["headlines"].extend(fallback_headlines[len(result["headlines"]) : 3])
    result["legacyUnlocks"] = (
        filter_legacy_unlocks(result.get("legacyUnlocks")) or fallback["legacyUnlocks"]
    )
    if not isinstance(result.get("lastEmployee"), dict | type(None)):
        result["lastEmployee"] = fallback["lastEmployee"]
    truncate_paths(result, {("obituary",): 600})
    min_length_or_fallback(result, fallback, ("obituary",), 200)
    return result


def normalize_director_fallback(fallback: dict[str, Any]) -> dict[str, Any]:
    repaired = apply_aliases(repair_keys(fallback, DIRECTOR_KEYS))
    repaired = merge_shape(repaired, canonical_director_base())
    repaired["metricsDelta"] = clamp_metrics_delta(as_dict(repaired.get("metricsDelta")))
    rival = as_dict(repaired.get("rivalAction"))
    rival["expectedDamage"] = clamp_metrics_delta(as_dict(rival.get("expectedDamage")))
    repaired["rivalAction"] = rival
    truncate_paths(repaired, DIRECTOR_LIMITS)
    return repaired


def normalize_death_fallback(fallback: dict[str, Any]) -> dict[str, Any]:
    repaired = apply_aliases(repair_keys(fallback, DEATH_KEYS))
    repaired = merge_shape(repaired, canonical_death_base())
    repaired["legacyUnlocks"] = filter_legacy_unlocks(repaired.get("legacyUnlocks"))
    if not isinstance(repaired.get("lastEmployee"), dict | type(None)):
        repaired["lastEmployee"] = None
    return repaired


def repair_keys(value: Any, allowed: set[str]) -> Any:
    if isinstance(value, dict):
        repaired: dict[str, Any] = {}
        for raw_key, raw_value in value.items():
            key = str(raw_key)
            if key not in allowed:
                matches = get_close_matches(key, allowed, n=1, cutoff=0.82)
                key = matches[0] if matches else key
            repaired[key] = repair_keys(raw_value, allowed)
        return repaired
    if isinstance(value, list):
        return [repair_keys(item, allowed) for item in value]
    return value


def apply_aliases(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            FIELD_ALIASES.get(str(key), str(key)): apply_aliases(item)
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [apply_aliases(item) for item in value]
    return value


def merge_shape(source: Mapping[str, Any], fallback: Mapping[str, Any]) -> dict[str, Any]:
    merged: dict[str, Any] = {}
    for key, fallback_value in fallback.items():
        source_value = source.get(key)
        if isinstance(fallback_value, dict):
            merged[key] = merge_shape(as_dict(source_value), fallback_value)
        elif compatible(source_value, fallback_value):
            merged[key] = deepcopy(source_value)
        else:
            merged[key] = deepcopy(fallback_value)
    return merged


def compatible(value: Any, fallback: Any) -> bool:
    if value is None:
        return fallback is None
    if fallback is None:
        return True
    if isinstance(fallback, bool):
        return isinstance(value, bool)
    if isinstance(fallback, int):
        return isinstance(value, int) and not isinstance(value, bool)
    if isinstance(fallback, str):
        return isinstance(value, str)
    if isinstance(fallback, list):
        return isinstance(value, list)
    return isinstance(value, type(fallback))


def as_dict(value: Any) -> dict[Any, Any]:
    return value if isinstance(value, dict) else {}


def get_path(data: dict[str, Any], path: tuple[str, ...]) -> Any:
    current: Any = data
    for key in path:
        if not isinstance(current, dict):
            return None
        current = current.get(key)
    return current


def set_path(data: dict[str, Any], path: tuple[str, ...], value: Any) -> None:
    current = data
    for key in path[:-1]:
        next_value = current.setdefault(key, {})
        if not isinstance(next_value, dict):
            next_value = {}
            current[key] = next_value
        current = next_value
    current[path[-1]] = value


def clamp_int_path(data: dict[str, Any], path: tuple[str, ...], low: int, high: int) -> None:
    value = get_path(data, path)
    if isinstance(value, int) and not isinstance(value, bool):
        set_path(data, path, min(high, max(low, value)))


def literal_or_fallback(
    data: dict[str, Any],
    fallback: dict[str, Any],
    path: tuple[str, ...],
    allowed: set[str],
) -> None:
    if get_path(data, path) not in allowed:
        set_path(data, path, get_path(fallback, path))


def truncate_paths(data: dict[str, Any], limits: Mapping[tuple[str, ...], int]) -> None:
    for path, limit in limits.items():
        value = get_path(data, path)
        if isinstance(value, str) and len(value) > limit:
            set_path(data, path, value[:limit])


def min_length_or_fallback(
    data: dict[str, Any],
    fallback: dict[str, Any],
    path: tuple[str, ...],
    min_length: int,
) -> None:
    value = get_path(data, path)
    if not isinstance(value, str) or len(value) < min_length:
        set_path(data, path, get_path(fallback, path))


def normalize_scores(value: dict[Any, Any]) -> dict[str, int]:
    aliased: dict[str, Any] = {}
    for k, v in value.items():
        canonical = SCORE_ALIASES.get(k, k)
        aliased.setdefault(canonical, v)
    scores: dict[str, int] = {}
    for key in SCORE_KEYS:
        raw_score = aliased.get(key, 50)
        score = raw_score if isinstance(raw_score, int) and not isinstance(raw_score, bool) else 50
        scores[key] = min(100, max(0, score))
    return scores


def filter_legacy_unlocks(value: Any) -> list[str]:
    allowed = {item.value for item in LegacyType}
    if not isinstance(value, list):
        return []
    filtered: list[str] = []
    for item in value:
        legacy = item.get("type") if isinstance(item, dict) else item
        if isinstance(legacy, str) and legacy in allowed:
            filtered.append(legacy)
    return filtered
