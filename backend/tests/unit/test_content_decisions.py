"""Tests for decision content templates."""

from __future__ import annotations

from app.content import DECISION_CARDS, sample_decision_cards
from app.domain import DecisionCategory, Stats


def test_decision_categories_are_fully_covered() -> None:
    categories = {card["category"] for card in DECISION_CARDS}
    assert categories == {category.value for category in DecisionCategory}


def test_sample_decision_cards_returns_three_unique_cards() -> None:
    cards = sample_decision_cards(n=3, rng_seed=11)

    assert len(cards) == 3
    assert len({card["id"] for card in cards}) == 3


def test_sample_decision_cards_filters_applicable_when() -> None:
    stats = Stats(CASH=25, MORALE=50, BOARD=50, FACE=50)
    cards = sample_decision_cards(n=12, current_stats=stats, rng_seed=7)

    assert "D_KILL_PRODUCT_01" not in {card["id"] for card in cards}
