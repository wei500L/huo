"""Tests for company content templates."""

from __future__ import annotations

from app.content import COMPANY_TEMPLATES, get_company_template_by_id, sample_company_template


def test_company_templates_are_complete() -> None:
    assert len(COMPANY_TEMPLATES) == 6
    for template in COMPANY_TEMPLATES:
        assert {
            "template_id",
            "name_pool",
            "business",
            "absurdity",
            "founding_motto",
            "death_causes",
            "starting_promises",
            "stats_modifiers",
        } <= template.keys()
        assert 2 <= len(template["name_pool"]) <= 3
        assert 2 <= len(template["death_causes"]) <= 3
        assert set(template["stats_modifiers"]) == {"CASH", "MORALE", "BOARD", "FACE"}


def test_company_template_lookup_and_sampling_are_reproducible() -> None:
    assert get_company_template_by_id("C-03") is not None
    assert get_company_template_by_id("missing") is None
    assert sample_company_template(rng_seed=42) == sample_company_template(rng_seed=42)
