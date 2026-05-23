"""Tests for the meta progress domain model."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.domain import DeathLogEntry, LegacyType, ManagementStyle, MetaProgress
from tests.factories import build_legacy_unlock, build_meta_progress


def test_register_run_end_deduplicates_legacy_types_and_styles() -> None:
    progress = build_meta_progress(
        unlocked_legacies=[build_legacy_unlock(type=LegacyType.PR_EXPERIENCE)],
        unlocked_styles=[ManagementStyle.FACE_KEEPER],
        total_runs=2,
    )
    entry = DeathLogEntry(
        run_id="R-0001",
        company_name="星火集团",
        business="卖月亮咖啡",
        died_at_quarter=4,
        death_reason=None,
        obituary="公司撑过了 Q4。",
        biggest_mistake_decision_id=None,
        last_employee_quote=None,
        headlines=["撑过 Q4"],
    )

    updated = progress.register_run_end(
        entry=entry,
        new_legacies=[
            build_legacy_unlock(type=LegacyType.PR_EXPERIENCE, label_zh="重复遗产"),
            build_legacy_unlock(type=LegacyType.ORG_KNOWHOW),
            build_legacy_unlock(type=LegacyType.ORG_KNOWHOW, label_zh="重复组织"),
        ],
        new_styles=[
            ManagementStyle.FACE_KEEPER,
            ManagementStyle.IRON_LAYOFF,
            ManagementStyle.IRON_LAYOFF,
        ],
    )

    assert isinstance(updated, MetaProgress)
    assert [unlock.type for unlock in updated.unlocked_legacies] == [
        LegacyType.PR_EXPERIENCE,
        LegacyType.ORG_KNOWHOW,
    ]
    assert updated.unlocked_styles == [ManagementStyle.FACE_KEEPER, ManagementStyle.IRON_LAYOFF]
    assert updated.total_runs == 3
    assert updated.death_log[-1] == entry


def test_death_log_entry_headlines_max_three() -> None:
    with pytest.raises(ValidationError):
        DeathLogEntry(
            run_id="R-0002",
            company_name="星火集团",
            business="卖月亮咖啡",
            died_at_quarter=1,
            death_reason=None,
            obituary="Q1 就倒下了。",
            biggest_mistake_decision_id=None,
            last_employee_quote=None,
            headlines=["a", "b", "c", "d"],
        )


@pytest.mark.parametrize(
    "legacy_type",
    [
        LegacyType.PR_EXPERIENCE,
        LegacyType.FUNDING_PITCH,
        LegacyType.ORG_KNOWHOW,
        LegacyType.PRODUCT_TASTE,
        LegacyType.MEDIA_NERVE,
        LegacyType.EMPLOYEE_TRUST,
        LegacyType.INDUSTRY_INTEL,
    ],
)
def test_legacy_type_members_cover_design(legacy_type: LegacyType) -> None:
    assert legacy_type.value == legacy_type.name


@pytest.mark.parametrize(
    "style",
    [
        ManagementStyle.IRON_LAYOFF,
        ManagementStyle.STORY_MASTER,
        ManagementStyle.DATA_FREAK,
        ManagementStyle.FACE_KEEPER,
        ManagementStyle.SURVIVAL_PRO,
    ],
)
def test_management_style_members_cover_design(style: ManagementStyle) -> None:
    assert style.value == style.name


def test_legacy_unlock_length_constraints() -> None:
    with pytest.raises(ValidationError):
        build_legacy_unlock(label_zh="超长遗产名称超出长度限制测试")

    with pytest.raises(ValidationError):
        build_legacy_unlock(effect_summary="x" * 41)
