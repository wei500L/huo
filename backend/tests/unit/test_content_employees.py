"""Tests for employee content templates."""

from __future__ import annotations

from app.content import EMPLOYEE_TEMPLATES, get_employee_template_by_id, sample_employee_set


def test_employee_templates_cover_all_roles() -> None:
    assert len(EMPLOYEE_TEMPLATES) == 12
    assert {template["role"] for template in EMPLOYEE_TEMPLATES} == {
        "CEO 助理",
        "CFO",
        "CTO",
        "产品负责人",
        "HR 总监",
        "销售总监",
        "核心工程师 A",
        "核心工程师 B",
        "摸鱼员工",
        "激进员工",
        "老臣员工",
        "叛逃种子员工",
    }
    for template in EMPLOYEE_TEMPLATES:
        assert len(template["name_pool"]) >= 3


def test_employee_template_lookup_and_sampling_are_reproducible() -> None:
    assert get_employee_template_by_id("E-T-05") is not None
    assert get_employee_template_by_id("missing") is None
    assert sample_employee_set(rng_seed=9) == sample_employee_set(rng_seed=9)
