"""Domain-level test factories."""

from __future__ import annotations

from datetime import UTC, datetime
from random import Random
from uuid import UUID, uuid4

from app.content.companies import sample_company_template
from app.content.employees import sample_employee_set
from app.domain import (
    BoomerangSeed,
    Company,
    DeathCause,
    DecisionCard,
    DecisionCategory,
    Employee,
    Faction,
    Mood,
    PersonalityTag,
    Relationship,
    Stats,
    StatsDelta,
)

__all__ = (
    "build_company",
    "build_decision_card",
    "build_employee",
    "build_employees",
    "build_stats",
)

_FIXED_NOW = datetime(2026, 5, 23, 9, 0, tzinfo=UTC)
_DEFAULT_COMPANY = {
    "name": "星火集团",
    "business": "卖月亮咖啡",
    "absurdity": 3,
    "founding_motto": "先活下去再说",
    "death_causes": [
        DeathCause(category="financial", description="现金流断裂后直接停摆"),
        DeathCause(category="trust", description="员工和董事会同时失去信任"),
    ],
    "starting_promises": [],
    "founded_year": 2024,
}


def build_stats(seed: int | None = None, **overrides: object) -> Stats:
    values: dict[str, object] = (
        Stats.starting(seed=seed).model_dump() if seed is not None else {
            "CASH": 45,
            "MORALE": 50,
            "BOARD": 50,
            "FACE": 60,
        }
    )
    values.update(overrides)
    return Stats(**values)


def build_company(seed: int | None = None, **overrides: object) -> Company:
    if seed is None:
        values: dict[str, object] = dict(_DEFAULT_COMPANY)
        values["id"] = str(uuid4())
        values.update(overrides)
        return Company.from_template(values)

    rng = Random(seed)
    template = sample_company_template(rng.randrange(2**32))
    values = {
        "id": _seed_uuid(seed, prefix="company"),
        "name": str(rng.choice(list(template["name_pool"]))),
        "business": str(template["business"]),
        "absurdity": int(template["absurdity"]),
        "founding_motto": str(template["founding_motto"]),
        "death_causes": [DeathCause(**cause) for cause in template["death_causes"]],
        "starting_promises": [str(promise) for promise in template["starting_promises"]],
        "founded_year": int(template["founded_year"]),
    }
    values.update(overrides)
    return Company(**values)


def build_decision_card(seed: int | None = None, **overrides: object) -> DecisionCard:
    rng = Random(seed)
    values: dict[str, object] = {
        "id": f"D_{rng.randrange(1_000_000):06d}" if seed is not None else "D_LAYOFF_01",
        "category": DecisionCategory.LAYOFF,
        "title": "裁员止血",
        "description": "先砍人头再谈效率",
        "immediate_effect": StatsDelta(CASH=8, MORALE=-10, BOARD=2, FACE=-4),
        "flavor": "账面好看，气氛难看",
        "long_term_hint": "三季后会反噬",
        "boomerang_seeds": [
            BoomerangSeed(
                delay_quarters=2,
                probability=0.6,
                description="核心员工开始流失",
                effect=StatsDelta(MORALE=-5, FACE=-3),
            ),
        ],
    }
    values.update(overrides)
    return DecisionCard(**values)


def build_employee(seed: int | None = None, **overrides: object) -> Employee:
    rng = Random(seed)
    values: dict[str, object] = {
        "id": _employee_id(seed),
        "name": rng.choice(["张三", "李四", "王五"]) if seed is not None else "张三",
        "role": "后端工程师",
        "competence": 65,
        "loyalty": 55,
        "stress": 40,
        "personality_tag": PersonalityTag.GOOD_PERSON,
        "faction": Faction.NEUTRAL,
        "relationships": [],
        "hidden_secrets": [],
        "attitude_to_player": 50,
        "current_goal": None,
        "mood": Mood.NEUTRAL,
    }
    values.update(overrides)
    return Employee(**values)


def build_employees(count: int = 12, seed: int | None = None) -> list[Employee]:
    templates = sample_employee_set(seed)[:count]
    rng = Random(seed)
    employees: list[Employee] = []
    for index, template in enumerate(templates):
        employee_rng = Random(rng.randrange(2**32) ^ index)
        loyalty = _sample_range(template, "loyalty_range", employee_rng)
        stress = _sample_range(template, "stress_range", employee_rng)
        employee = Employee(
            id=_employee_id(employee_rng.randrange(2**32)),
            name=str(employee_rng.choice(template["name_pool"])),
            role=str(template["role"]),
            competence=_sample_range(template, "competence_range", employee_rng),
            loyalty=loyalty,
            stress=stress,
            personality_tag=PersonalityTag(str(template["personality_tag"])),
            faction=Faction(str(template["faction"])),
            relationships=[],
            hidden_secrets=_sample_hidden_secrets(template, employee_rng),
            attitude_to_player=_sample_attitude(loyalty, employee_rng),
            current_goal=None,
            mood=_derive_mood(loyalty, stress),
        )
        employees.append(employee)
    resolved = _resolve_employee_relationships(employees, templates)
    return resolved


def _derive_mood(loyalty: int, stress: int) -> Mood:
    if loyalty > 70:
        return Mood.HOPEFUL
    if stress > 80 and loyalty < 30:
        return Mood.NUMB
    if loyalty < 30 and stress > 60:
        return Mood.ANGRY
    if stress > 60:
        return Mood.ANXIOUS
    return Mood.NEUTRAL


def _sample_range(template: dict[str, object], field: str, rng: Random) -> int:
    low, high = template[field]  # type: ignore[index]
    return rng.randint(int(low), int(high))


def _sample_hidden_secrets(template: dict[str, object], rng: Random) -> list[str]:
    pool = [str(item) for item in template.get("hidden_secrets_pool", [])]
    if not pool:
        return []
    count = rng.randint(0, min(2, len(pool)))
    return rng.sample(pool, count)


def _sample_attitude(loyalty: int, rng: Random) -> int:
    return max(0, min(100, loyalty + rng.randint(-10, 10)))


def _resolve_employee_relationships(
    employees: list[Employee],
    templates: list[dict[str, object]],
) -> list[Employee]:
    template_to_id = {
        str(template["template_id"]): employee.id
        for employee, template in zip(employees, templates, strict=True)
    }
    resolved: list[Employee] = []
    for employee, template in zip(employees, templates, strict=True):
        relationships = [
            Relationship(
                target_id=template_to_id[
                    str(seed.get("target_template_id") or seed["template_id"])
                ],
                type=str(seed["type"]),
                strength=int(seed["strength"]),
            )
            for seed in template.get("relationships_seed", [])
        ]
        resolved.append(employee.model_copy(update={"relationships": relationships}))
    return resolved


def _seed_uuid(seed: int | None, prefix: str) -> str:
    if seed is None:
        return str(uuid4())
    rng = Random(f"{prefix}:{seed}")
    return str(UUID(int=rng.getrandbits(128), version=4))


def _employee_id(seed: int | None) -> str:
    if seed is None:
        return f"E-{uuid4().hex[:8]}"
    rng = Random(f"employee:{seed}")
    return f"E-{rng.getrandbits(32):08x}"


def _prefixed_hex(prefix: str, seed: int | None) -> str:
    if seed is None:
        return f"{prefix}-{uuid4().hex[:8]}"
    rng = Random(f"{prefix}:{seed}")
    return f"{prefix}-{rng.getrandbits(32):08x}"
