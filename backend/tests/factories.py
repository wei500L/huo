"""Test factories."""

from __future__ import annotations

from app.domain import Company, DeathCause, Stats

__all__ = ("build_company", "build_stats")


def build_stats(**overrides: object) -> Stats:
    """Build a valid stats object for tests."""

    values: dict[str, object] = {
        "CASH": 45,
        "MORALE": 50,
        "BOARD": 50,
        "FACE": 60,
    }
    values.update(overrides)
    return Stats(**values)


def build_company(**overrides: object) -> Company:
    """Build a valid company object for tests."""

    values: dict[str, object] = {
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
    values.update(overrides)
    return Company.from_template(values)
