"""Unit tests for promise extraction."""

from __future__ import annotations

import pytest

from app.domain import PromiseSource
from app.services.promise_extractor import extract_promises


@pytest.mark.parametrize(
    "text",
    [
        "Q3 我们会把 GMV 翻倍。",
        "下季度销售增长 30%。",
        "明年营收做到2亿。",
        "利润增长15%，董事会会看到结果。",
        "用户规模增长 50%。",
        "融资规模达到1亿。",
        "估值增长 80%。",
        "现金流下季度增长20%。",
        "员工士气提升30%。",
        "品牌口碑增长25%。",
        "Q4 销售额做到3千万。",
        "MAU增长40%，留存提升20%。",
    ],
)
def test_positive_promise_examples_are_extracted(text: str) -> None:
    promises = extract_promises(text, PromiseSource.FREE_TEXT, quarter=2)

    assert len(promises) == 1
    assert promises[0].fulfilled is None
    assert promises[0].parsed is not None


def test_positive_suite_extracts_at_least_nine_of_twelve() -> None:
    examples = [
        "Q3 我们会把 GMV 翻倍。",
        "下季度销售增长 30%。",
        "明年营收做到2亿。",
        "利润增长15%，董事会会看到结果。",
        "用户规模增长 50%。",
        "融资规模达到1亿。",
        "估值增长 80%。",
        "现金流下季度增长20%。",
        "员工士气提升30%。",
        "品牌口碑增长25%。",
        "Q4 销售额做到3千万。",
        "MAU增长40%，留存提升20%。",
    ]

    extracted_count = sum(
        1 for example in examples if extract_promises(example, PromiseSource.FREE_TEXT, quarter=2)
    )

    assert extracted_count >= 9


@pytest.mark.parametrize(
    "text",
    [
        "今天天气不错",
        "员工辛苦了",
        "",
        "我们会增长 30%",
        "GMV 和销售都会改善",
    ],
)
def test_counterexamples_extract_no_promises(text: str) -> None:
    assert extract_promises(text, PromiseSource.FREE_TEXT, quarter=1) == []


@pytest.mark.parametrize("text", [None, ""])
def test_empty_boundary_returns_empty_list(text: str | None) -> None:
    assert extract_promises(text, PromiseSource.FREE_TEXT, quarter=1) == []


def test_parses_deadline_target_and_metric() -> None:
    promises = extract_promises("Q3 我们会把 GMV 翻倍。", PromiseSource.DECISION_FLAVOR, 1)

    assert len(promises) == 1
    parsed = promises[0].parsed
    assert parsed is not None
    assert parsed.deadline_quarter == 3
    assert parsed.target_expr == "翻倍"
    assert parsed.metric == "SALES_HINT"
