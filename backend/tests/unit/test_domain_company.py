"""Tests for the company domain model."""

from __future__ import annotations

from uuid import UUID

import pytest
from pydantic import ValidationError

from app.domain import Company
from tests.factories import build_company


def test_company_from_template_accepts_valid_fields() -> None:
    company = Company.from_template(_valid_template(), rng_seed=42)

    assert len(company.name) <= 20
    assert len(company.business) <= 30
    assert 1 <= company.absurdity <= 5
    assert len(company.founding_motto) <= 30
    assert 2 <= len(company.death_causes) <= 3
    assert len(company.starting_promises) <= 3
    assert 2020 <= company.founded_year <= 2029
    assert UUID(company.id).version == 4


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("name", "超长公司" * 6),
        ("business", "荒诞业务" * 8),
        ("founding_motto", "创始口号" * 8),
        ("starting_promises", ["破承诺" * 11]),
        (
            "death_causes",
            [
                {"category": "financial", "description": "现金流断裂"},
                {"category": "trust", "description": "死因描述" * 21},
            ],
        ),
    ],
)
def test_company_from_template_length_constraints(field: str, value: object) -> None:
    template = _valid_template()
    template[field] = value

    with pytest.raises(ValidationError):
        Company.from_template(template, rng_seed=42)


@pytest.mark.parametrize("absurdity", [0, 6])
def test_company_rejects_invalid_absurdity(absurdity: int) -> None:
    template = _valid_template()
    template["absurdity"] = absurdity

    with pytest.raises(ValidationError):
        Company.from_template(template)


def test_company_ids_are_unique_uuid4_values() -> None:
    companies = [build_company() for _ in range(100)]
    ids = {company.id for company in companies}

    assert len(ids) == 100
    assert all(UUID(company_id).version == 4 for company_id in ids)


def _valid_template() -> dict[str, object]:
    return {
        "name": ["星火集团", "蓝塔科技"],
        "business": ["卖月亮咖啡", "订阅式董事会道歉"],
        "absurdity": [2, 3, 4],
        "founding_motto": ["先活下去再说", "让现金流重新做人"],
        "death_causes": [
            {"category": "financial", "description": "现金流断裂后直接停摆"},
            {"category": "trust", "description": "员工和董事会同时失去信任"},
            {"category": "market", "description": "市场突然发现产品只是情绪价值"},
        ],
        "starting_promises": ["永不裁员", "绝不画饼", "下季度一定盈利"],
        "founded_year": [2023, 2024, 2025],
    }
