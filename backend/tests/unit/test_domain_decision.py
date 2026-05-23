"""Tests for the decision domain models."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.domain import BoomerangSeed, DecisionCategory, StatsDelta
from tests.factories import build_decision_card


def test_decision_card_field_length_boundaries() -> None:
    card = build_decision_card(
        title="测" * 14,
        description="说" * 40,
        flavor="味" * 30,
        long_term_hint="后" * 30,
    )

    assert len(card.title) == 14
    assert len(card.description) == 40
    assert len(card.flavor) == 30
    assert card.long_term_hint is not None
    assert len(card.long_term_hint) == 30


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("title", "测" * 15),
        ("description", "说" * 41),
        ("flavor", "味" * 31),
        ("long_term_hint", "后" * 31),
    ],
)
def test_decision_card_rejects_overlong_fields(field: str, value: str) -> None:
    kwargs = {field: value}

    with pytest.raises(ValidationError):
        build_decision_card(**kwargs)


@pytest.mark.parametrize("probability", [-0.1, 1.1])
def test_boomerang_seed_probability_out_of_bounds(probability: float) -> None:
    with pytest.raises(ValidationError):
        BoomerangSeed(
            delay_quarters=1,
            probability=probability,
            description="延迟反噬",
            effect=StatsDelta(CASH=-1),
        )


@pytest.mark.parametrize(
    ("category", "expected"),
    [
        (DecisionCategory.FUNDING, "融资"),
        (DecisionCategory.LAYOFF, "裁员"),
        (DecisionCategory.SELL_ASSET, "卖资产"),
        (DecisionCategory.PIVOT, "产品转型"),
        (DecisionCategory.KILL_PRODUCT, "砍产品线"),
        (DecisionCategory.PRICE_WAR, "价格战"),
        (DecisionCategory.SOOTHE, "安抚员工"),
        (DecisionCategory.SWAP_EXEC, "换高管"),
        (DecisionCategory.HIDE_BAD_NEWS, "隐瞒坏消息"),
        (DecisionCategory.DELAY_BOARD, "争取董事会时间"),
        (DecisionCategory.NEGOTIATE_RIVAL, "与对手谈判"),
        (DecisionCategory.HUMILIATING_TERM, "接受屈辱条款"),
    ],
)
def test_decision_category_label_zh(category: DecisionCategory, expected: str) -> None:
    assert category.label_zh == expected
