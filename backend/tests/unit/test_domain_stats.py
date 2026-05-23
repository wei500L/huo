"""Tests for the stats domain model."""

from __future__ import annotations

import pytest

from app.domain import DeathReason, Stats, StatsDelta


def test_starting_stats_are_within_ranges() -> None:
    stats = Stats.starting()

    assert 30 <= stats.CASH <= 60
    assert 40 <= stats.MORALE <= 60
    assert 40 <= stats.BOARD <= 60
    assert 50 <= stats.FACE <= 70


def test_starting_stats_are_reproducible_with_seed() -> None:
    first = Stats.starting(seed=42)
    second = Stats.starting(seed=42)

    assert first == second


@pytest.mark.parametrize(
    ("delta", "expected"),
    [
        (StatsDelta(CASH=10, MORALE=-5, BOARD=0, FACE=None), Stats(CASH=60, MORALE=45, BOARD=50, FACE=60)),
        (StatsDelta(CASH=-20, MORALE=-80, BOARD=-1, FACE=-100), Stats(CASH=30, MORALE=0, BOARD=49, FACE=0)),
        (StatsDelta(CASH=1000, MORALE=1000, BOARD=1000, FACE=1000), Stats(CASH=100, MORALE=100, BOARD=100, FACE=100)),
    ],
)
def test_apply_delta_clamps_and_handles_signs(delta: StatsDelta, expected: Stats) -> None:
    base = Stats(CASH=50, MORALE=50, BOARD=50, FACE=60)

    assert base.apply_delta(delta) == expected
    assert base == Stats(CASH=50, MORALE=50, BOARD=50, FACE=60)


@pytest.mark.parametrize(
    ("stats", "expected"),
    [
        (Stats(CASH=0, MORALE=50, BOARD=50, FACE=50), DeathReason.BANKRUPTCY),
        (Stats(CASH=10, MORALE=10, BOARD=50, FACE=50), DeathReason.MORALE_COLLAPSE),
        (Stats(CASH=10, MORALE=50, BOARD=5, FACE=50), DeathReason.OUSTED),
        (Stats(CASH=10, MORALE=50, BOARD=50, FACE=0), DeathReason.DISGRACE),
        (Stats(CASH=10, MORALE=50, BOARD=50, FACE=50), None),
    ],
)
def test_is_dead_thresholds(stats: Stats, expected: DeathReason | None) -> None:
    assert stats.is_dead() == expected


@pytest.mark.parametrize(
    ("stats", "expected"),
    [
        (Stats(CASH=0, MORALE=0, BOARD=0, FACE=0), DeathReason.BANKRUPTCY),
        (Stats(CASH=1, MORALE=0, BOARD=0, FACE=0), DeathReason.DISGRACE),
        (Stats(CASH=1, MORALE=0, BOARD=0, FACE=1), DeathReason.OUSTED),
        (Stats(CASH=1, MORALE=10, BOARD=6, FACE=1), DeathReason.MORALE_COLLAPSE),
    ],
)
def test_is_dead_priority(stats: Stats, expected: DeathReason) -> None:
    assert stats.is_dead() == expected


def test_stats_delta_merge_and_as_dict() -> None:
    first = StatsDelta(CASH=1, MORALE=None, BOARD=-2, FACE=0)
    second = StatsDelta(CASH=3, MORALE=4, BOARD=None, FACE=None)

    merged = first.merge(second)

    assert merged == StatsDelta(CASH=4, MORALE=4, BOARD=-2, FACE=0)
    assert merged.as_dict() == {"CASH": 4, "MORALE": 4, "BOARD": -2, "FACE": 0}
