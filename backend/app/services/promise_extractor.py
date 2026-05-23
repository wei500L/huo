"""Regex based promise extraction."""

from __future__ import annotations

import re
from typing import Literal
from uuid import uuid4

from app.domain import Promise, PromiseSource, PromiseTarget

__all__ = ("PROMISE_PATTERNS", "extract_promises")

PROMISE_PATTERNS: list[tuple[re.Pattern[str], dict[str, str]]] = [
    (re.compile(r"(?P<deadline>Q(?P<qnum>[1-4]))", re.IGNORECASE), {"kind": "deadline"}),
    (re.compile(r"(?P<deadline>下季度|明年)"), {"kind": "deadline"}),
    (re.compile(r"(?P<target>翻倍)"), {"kind": "target"}),
    (re.compile(r"(?P<target>(?:\+|增长\s*)?\d{1,3}%)"), {"kind": "target"}),
    (re.compile(r"(?P<target>\d+(?:\.\d+)?\s*(?:亿|百万|千万))"), {"kind": "target"}),
    (
        re.compile(
            r"(?P<metric>GMV|销售|营收|收入|利润|用户|DAU|MAU|订单|留存|融资|估值|"
            r"现金流|现金|成本|毛利|董事会|投资人|股东|士气|员工|团队|口碑|舆论|"
            r"媒体|品牌|声誉)",
            re.IGNORECASE,
        ),
        {"kind": "metric"},
    ),
]

_SENTENCE_SPLIT_RE = re.compile(r"[。！？\n]+")

PromiseMetric = Literal["CASH", "MORALE", "BOARD", "FACE", "SALES_HINT"]

_METRIC_TO_TARGET: tuple[tuple[tuple[str, ...], PromiseMetric], ...] = (
    (("融资", "估值", "现金流", "现金", "营收", "收入", "利润", "成本", "毛利"), "CASH"),
    (("士气", "员工", "团队"), "MORALE"),
    (("董事会", "投资人", "股东"), "BOARD"),
    (("口碑", "舆论", "媒体", "品牌", "声誉"), "FACE"),
    (("gmv", "销售", "用户", "dau", "mau", "订单", "留存"), "SALES_HINT"),
)


def extract_promises(
    text: str | None,
    source: PromiseSource,
    quarter: int,
) -> list[Promise]:
    if not text:
        return []

    promises: list[Promise] = []
    for sentence in _split_sentences(text):
        parsed = _extract_sentence(sentence, quarter)
        if parsed is None:
            continue
        promises.append(
            Promise(
                id=f"PM-{uuid4().hex[:10]}",
                quarter_made=quarter,
                source=source,
                text=sentence[:80],
                parsed=parsed,
                fulfilled=None,
            ),
        )
    return promises


def _split_sentences(text: str) -> list[str]:
    return [sentence.strip() for sentence in _SENTENCE_SPLIT_RE.split(text) if sentence.strip()]


def _extract_sentence(sentence: str, quarter: int) -> PromiseTarget | None:
    target_expr: str | None = None
    deadline_quarter: int | None = None
    metric_word: str | None = None

    for pattern, template in PROMISE_PATTERNS:
        for match in pattern.finditer(sentence):
            kind = template["kind"]
            if kind == "target" and target_expr is None:
                target_expr = match.group("target").replace(" ", "")
            elif kind == "deadline" and deadline_quarter is None:
                deadline_quarter = _parse_deadline(match.group("deadline"), quarter)
            elif kind == "metric" and metric_word is None:
                metric_word = match.group("metric")

    if target_expr is None or metric_word is None:
        return None

    return PromiseTarget(
        metric=_map_metric(metric_word),
        target_expr=target_expr,
        deadline_quarter=deadline_quarter,
    )


def _parse_deadline(value: str, quarter: int) -> int | None:
    normalized = value.upper()
    if normalized.startswith("Q") and normalized[1:].isdigit():
        return int(normalized[1:])
    if value == "下季度":
        next_quarter = quarter + 1
        return next_quarter if next_quarter <= 4 else None
    return None


def _map_metric(metric_word: str) -> PromiseMetric:
    normalized = metric_word.lower()
    for keywords, target in _METRIC_TO_TARGET:
        if normalized in keywords:
            return target
    return "SALES_HINT"
