"""Shared helpers for settlement rule resolvers."""

from __future__ import annotations

import logging
import re
from collections.abc import Callable, Mapping
from difflib import get_close_matches
from hashlib import sha256

from app.domain import StatsDelta

logger = logging.getLogger(__name__)

MEDIA_OUTLET_POOL: tuple[str, ...] = (
    "36 氪",
    "彭博体",
    "晚点 LatePost",
    "虎嗅",
    "钛媒体",
    "脉脉自媒体",
)

BOARD_VOTE_POOL: tuple[str, ...] = ("approve", "oppose", "abstain")
GOSSIP_MOOD_POOL: tuple[str, ...] = (
    "anxious",
    "angry",
    "tired",
    "hopeful",
    "numb",
    "excited",
    "in_love",
    "neutral",
)
RIVAL_ACTION_POOL: tuple[str, ...] = (
    "price_war",
    "poach",
    "launch",
    "pr_attack",
    "wait",
    "acquisition_rumor",
)
MEDIA_TONE_POOL: tuple[str, ...] = ("positive", "neutral", "negative", "mocking")

_OUTLET_ALIASES: dict[str, str] = {
    "36kr": "36 氪",
    "36k": "36 氪",
    "36氪": "36 氪",
    "latepost": "晚点 LatePost",
    "晚点": "晚点 LatePost",
    "huxiu": "虎嗅",
    "虎嗅": "虎嗅",
    "blomberg": "彭博体",
    "bloomberg": "彭博体",
    "彭博": "彭博体",
    "tmtpost": "钛媒体",
    "钛媒体": "钛媒体",
    "maimai": "脉脉自媒体",
    "脉脉": "脉脉自媒体",
}


def clamp_int(value: object, low: int, high: int, *, fallback: int = 0) -> int:
    """Clamp a possibly invalid value to a bounded integer."""

    if isinstance(value, bool) or not isinstance(value, int):
        return fallback
    return max(low, min(high, value))


def clamp_text(value: object, limit: int) -> str:
    """Trim text to a hard length limit."""

    text = str(value).strip()
    if len(text) <= limit:
        return text
    return text[:limit].rstrip()


def normalize_choice(
    value: object,
    allowed: tuple[str, ...],
    *,
    aliases: Mapping[str, str] | None = None,
    fallback: str | None = None,
    kind: str = "value",
) -> str:
    """Normalize a free-form string to a whitelisted literal."""

    default = fallback or allowed[0]
    raw = str(value).strip()
    if raw in allowed:
        return raw

    normalized = _normalize_token(raw)
    if aliases is not None:
        alias = aliases.get(raw) or aliases.get(normalized) or aliases.get(raw.lower())
        if alias in allowed:
            _log_normalization(kind, raw, alias)
            return alias

    match = get_close_matches(raw, list(allowed), n=1, cutoff=0.55)
    if match:
        _log_normalization(kind, raw, match[0])
        return match[0]

    _log_normalization(kind, raw, default)
    return default


def normalize_outlet(value: object) -> str:
    """Clamp outlet to the canonical outlet pool."""

    return normalize_choice(
        value,
        MEDIA_OUTLET_POOL,
        aliases=_OUTLET_ALIASES,
        kind="outlet",
    )


def normalize_vote(value: object) -> str:
    return normalize_choice(value, BOARD_VOTE_POOL, fallback="abstain", kind="vote")


def normalize_mood(value: object) -> str:
    return normalize_choice(value, GOSSIP_MOOD_POOL, fallback="anxious", kind="mood")


def normalize_action(value: object) -> str:
    return normalize_choice(value, RIVAL_ACTION_POOL, fallback="wait", kind="action")


def normalize_tone(value: object) -> str:
    return normalize_choice(value, MEDIA_TONE_POOL, fallback="neutral", kind="tone")


def stats_delta_from_mapping(value: Mapping[str, object]) -> StatsDelta:
    """Build a dense StatsDelta from a mapping with missing keys defaulted to zero."""

    return StatsDelta(
        CASH=clamp_int(value.get("CASH"), -10_000, 10_000),
        MORALE=clamp_int(value.get("MORALE"), -10_000, 10_000),
        BOARD=clamp_int(value.get("BOARD"), -10_000, 10_000),
        FACE=clamp_int(value.get("FACE"), -10_000, 10_000),
    )


def merge_stats_deltas(*deltas: StatsDelta) -> StatsDelta:
    """Merge sparse or dense deltas into one dense delta."""

    return StatsDelta(
        CASH=sum(_delta_value(delta.CASH) for delta in deltas),
        MORALE=sum(_delta_value(delta.MORALE) for delta in deltas),
        BOARD=sum(_delta_value(delta.BOARD) for delta in deltas),
        FACE=sum(_delta_value(delta.FACE) for delta in deltas),
    )


def build_stable_id(*parts: object, prefix: str = "M", length: int = 10) -> str:
    """Build a deterministic identifier from stable inputs."""

    payload = "|".join(str(part) for part in parts)
    digest = sha256(payload.encode("utf-8")).hexdigest()[:length]
    return f"{prefix}-{digest}"


LegacyBuffRule = Callable[[StatsDelta], StatsDelta]


def _face_keeper_rule(raw_metrics_delta: StatsDelta) -> StatsDelta:
    face = raw_metrics_delta.FACE or 0
    if face >= 0:
        return StatsDelta(CASH=0, MORALE=0, BOARD=0, FACE=0)
    buffered = int(face * 0.75)
    return StatsDelta(CASH=0, MORALE=0, BOARD=0, FACE=buffered - face)


LEGACY_BUFF_TABLE: dict[str, LegacyBuffRule] = {
    "FACE-keep": _face_keeper_rule,
    "FACE_KEEPER": _face_keeper_rule,
}


def legacy_buff_delta(signature: str, raw_metrics_delta: StatsDelta) -> StatsDelta:
    """Apply settlement-time legacy adjustments from the meta buff signature."""

    if not signature.strip():
        return StatsDelta(CASH=0, MORALE=0, BOARD=0, FACE=0)

    adjustment = StatsDelta(CASH=0, MORALE=0, BOARD=0, FACE=0)
    for token in _split_signature(signature):
        rule = LEGACY_BUFF_TABLE.get(token)
        if rule is None:
            continue
        adjustment = merge_stats_deltas(adjustment, rule(raw_metrics_delta))
    return adjustment


def _delta_value(value: int | None) -> int:
    return 0 if value is None else value


def _normalize_token(value: str) -> str:
    return re.sub(r"[\s_\-]+", "", value).lower()


def _split_signature(signature: str) -> list[str]:
    return [part.strip() for part in signature.split("/") if part.strip()]


def _log_normalization(kind: str, raw: str, resolved: str) -> None:
    if raw == resolved:
        return
    logger.warning("normalized %s", kind, extra={"raw": raw, "resolved": resolved})
