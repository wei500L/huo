"""Transcript cleaning helpers."""

from __future__ import annotations

import re

from pydantic import BaseModel, ConfigDict, Field

from .brand_blacklist import find_brand_hits

__all__ = (
    "CleanResult",
    "clean_transcript",
    "POLITICS_EXTREME_PATTERNS",
    "PROFANITY_PATTERNS",
)

_PROFANITY_TOKENS = [f"FB_{index:03d}" for index in range(1, 11)]
_POLITICS_EXTREME_TOKENS = [f"PB_{index:03d}" for index in range(1, 6)]

# QA keeps these placeholder tokens in sync with the maintained term list.
PROFANITY_PATTERNS = [re.compile(re.escape(token), re.IGNORECASE) for token in _PROFANITY_TOKENS]
POLITICS_EXTREME_PATTERNS = [
    re.compile(re.escape(token), re.IGNORECASE) for token in _POLITICS_EXTREME_TOKENS
]


class CleanResult(BaseModel):
    """Sanitised transcript response."""

    model_config = ConfigDict(strict=True)

    cleaned: str
    rejected: bool
    flags: list[str] = Field(default_factory=list)
    replaced_count: int = 0
    hits: list[str] = Field(default_factory=list)


def clean_transcript(raw: str) -> CleanResult:
    """Clean a transcript and reject unsafe content when needed."""

    if len(raw.strip()) < 30:
        return CleanResult(cleaned=raw, rejected=True, flags=["too_short"])

    politics_hits = _collect_pattern_hits(raw, POLITICS_EXTREME_PATTERNS)
    if politics_hits:
        return CleanResult(
            cleaned=raw,
            rejected=True,
            flags=["politics_rejected"],
            hits=politics_hits,
        )

    cleaned = raw
    flags: list[str] = []
    hits: list[str] = []
    replaced_count = 0

    brand_hits = find_brand_hits(cleaned)
    if brand_hits:
        cleaned, brand_count, brand_names = _replace_spans(cleaned, brand_hits, "[品牌]")
        if brand_count > 0:
            flags.append("brand_replaced")
            replaced_count += brand_count
            hits.extend(brand_names)

    profanity_hits = _find_pattern_hits(cleaned, PROFANITY_PATTERNS)
    if profanity_hits:
        cleaned, profanity_count, profanity_names = _replace_spans(
            cleaned,
            profanity_hits,
            "[屏蔽]",
        )
        if profanity_count > 0:
            flags.append("profanity_filtered")
            replaced_count += profanity_count
            hits.extend(profanity_names)

    return CleanResult(
        cleaned=cleaned,
        rejected=False,
        flags=flags,
        replaced_count=replaced_count,
        hits=hits,
    )


def _collect_pattern_hits(text: str, patterns: list[re.Pattern[str]]) -> list[str]:
    hits: list[tuple[int, int, str]] = []
    for pattern in patterns:
        for match in pattern.finditer(text):
            hits.append((match.start(), match.end(), pattern.pattern))
    hits.sort(key=lambda item: (item[0], item[1], item[2]))
    return [hit for _, _, hit in hits]


def _find_pattern_hits(text: str, patterns: list[re.Pattern[str]]) -> list[tuple[int, int, str]]:
    hits: list[tuple[int, int, str]] = []
    for pattern in patterns:
        for match in pattern.finditer(text):
            hits.append((match.start(), match.end(), pattern.pattern))
    hits.sort(key=lambda item: (item[0], item[1], item[2]))
    return hits


def _replace_spans(
    text: str,
    spans: list[tuple[int, int, str]],
    replacement: str,
) -> tuple[str, int, list[str]]:
    if not spans:
        return text, 0, []

    rebuilt: list[str] = []
    hits: list[str] = []
    last_end = 0
    replaced_count = 0

    for start, end, hit in sorted(spans, key=lambda item: (item[0], item[1], item[2])):
        if start < last_end:
            continue
        rebuilt.append(text[last_end:start])
        rebuilt.append(replacement)
        last_end = end
        replaced_count += 1
        hits.append(hit)

    rebuilt.append(text[last_end:])
    return "".join(rebuilt), replaced_count, hits
