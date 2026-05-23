"""Tests for gossip pool templates."""

from __future__ import annotations

from collections import Counter

from app.content import GOSSIP_TEMPLATES, sample_gossip_lead
from app.domain import Employee, Faction, PersonalityTag


def _build_employee(employee_id: str, name: str, role: str) -> Employee:
    return Employee(
        id=employee_id,
        name=name,
        role=role,
        competence=60,
        loyalty=60,
        stress=20,
        personality_tag=PersonalityTag.GOOD_PERSON,
        faction=Faction.NEUTRAL,
        relationships=[],
        hidden_secrets=[],
        attitude_to_player=50,
        current_goal=None,
    )


def test_gossip_scenes_are_complete() -> None:
    assert set(GOSSIP_TEMPLATES) == {
        "tearoom",
        "elevator",
        "meeting_room",
        "workstation",
        "rooftop",
        "smoking_area",
    }
    for templates in GOSSIP_TEMPLATES.values():
        assert 4 <= len(templates) <= 6
        for template in templates:
            assert "{speaker}" in template["text_template"]
            assert "{role}" in template["text_template"]


def test_sample_gossip_lead_reliability_matches_distribution() -> None:
    employees = [
        _build_employee("E-00000001", "陈砚", "CFO"),
        _build_employee("E-00000002", "唐婉", "HR 总监"),
        _build_employee("E-00000003", "沈知远", "CTO"),
    ]
    counts: Counter[str] = Counter()
    for seed in range(1000):
        lead = sample_gossip_lead("tearoom", employees, rng_seed=seed)
        counts[lead["reliability"]] += 1
        assert lead["speaker_id"] in {employee.id for employee in employees}

    total = sum(counts.values())
    assert abs(counts["RUMOR"] / total - 0.3) < 0.05
    assert abs(counts["LIKELY"] / total - 0.5) < 0.05
    assert abs(counts["CONFIRMED"] / total - 0.2) < 0.05
