"""Tests for the employee, relationship, and gossip lead domain models."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.domain import Employee, GossipLead, GossipReliability, Mood, PersonalityTag
from tests.factories import build_employee, build_gossip_lead


@pytest.mark.parametrize(
    ("builder_kwargs", "expected"),
    [
        ({"loyalty": 90, "stress": 10}, Mood.HOPEFUL),
        ({"loyalty": 10, "stress": 90}, Mood.NUMB),
        ({"loyalty": 10, "stress": 70}, Mood.ANGRY),
        ({"loyalty": 50, "stress": 70}, Mood.ANXIOUS),
        (
            {
                "loyalty": 50,
                "stress": 10,
                "relationships": [
                    {"target_id": "E-aaaa1111", "type": "crush", "strength": 60},
                ],
            },
            Mood.IN_LOVE,
        ),
        ({"loyalty": 50, "stress": 10}, Mood.NEUTRAL),
    ],
)
def test_employee_derive_mood_cases(builder_kwargs: dict[str, object], expected: Mood) -> None:
    employee = build_employee(**builder_kwargs)

    assert employee.derive_mood() == expected


@pytest.mark.parametrize(
    ("loyalty", "delta", "expected"),
    [
        (50, 10, 60),
        (50, -20, 30),
        (95, 10, 100),
        (5, -20, 0),
    ],
)
def test_employee_with_loyalty_clamps(loyalty: int, delta: int, expected: int) -> None:
    employee = build_employee(loyalty=loyalty)

    updated = employee.with_loyalty(delta)

    assert updated.loyalty == expected
    assert employee.loyalty == loyalty


@pytest.mark.parametrize(
    ("stress", "delta", "expected"),
    [
        (50, 10, 60),
        (50, -20, 30),
        (95, 10, 100),
        (5, -20, 0),
    ],
)
def test_employee_with_stress_clamps(stress: int, delta: int, expected: int) -> None:
    employee = build_employee(stress=stress)

    updated = employee.with_stress(delta)

    assert updated.stress == expected
    assert employee.stress == stress


@pytest.mark.parametrize(
    ("loyalty", "attitude", "expected"),
    [
        (19, 15, True),
        (20, 15, False),
        (21, 15, False),
        (50, 14, True),
        (50, 15, False),
        (50, 16, False),
    ],
)
def test_employee_is_quitting_risk_boundaries(
    loyalty: int,
    attitude: int,
    expected: bool,
) -> None:
    employee = build_employee(loyalty=loyalty, attitude_to_player=attitude)

    assert employee.is_quitting_risk() is expected


@pytest.mark.parametrize(
    ("tag", "expected"),
    [
        (PersonalityTag.GOOD_PERSON, "老好人"),
        (PersonalityTag.SLACKER, "摸鱼"),
        (PersonalityTag.GO_GETTER, "卷王"),
        (PersonalityTag.VETERAN, "老臣"),
        (PersonalityTag.TROUBLEMAKER, "刺头"),
        (PersonalityTag.DEFECTOR, "叛逃种子"),
        (PersonalityTag.IN_LOVE, "恋爱中"),
        (PersonalityTag.RADICAL, "革命派"),
        (PersonalityTag.CAUTIOUS, "谨慎"),
    ],
)
def test_personality_tag_label_zh(tag: PersonalityTag, expected: str) -> None:
    assert tag.label_zh == expected


def test_employee_is_frozen() -> None:
    employee = build_employee()

    with pytest.raises(ValidationError):
        employee.new_field = "blocked"  # type: ignore[attr-defined]


def test_gossip_lead_truth_flag_is_independent_of_reliability() -> None:
    lead = build_gossip_lead(
        reliability=GossipReliability.CONFIRMED,
        is_truth=False,
    )

    assert lead.reliability == GossipReliability.CONFIRMED
    assert lead.is_truth is False


def test_top_level_domain_exports_are_available() -> None:
    assert Employee.__name__ == "Employee"
    assert GossipLead.__name__ == "GossipLead"
