"""Cross-run meta progress domain models."""

from __future__ import annotations

from collections.abc import Iterable
from enum import StrEnum
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, field_validator

from .stats import DeathReason

__all__ = (
    "DeathLogEntry",
    "LegacyType",
    "LegacyUnlock",
    "ManagementStyle",
    "MetaProgress",
)


class LegacyType(StrEnum):
    """Legacy unlock categories carried into the next run."""

    PR_EXPERIENCE = "PR_EXPERIENCE"
    FUNDING_PITCH = "FUNDING_PITCH"
    ORG_KNOWHOW = "ORG_KNOWHOW"
    PRODUCT_TASTE = "PRODUCT_TASTE"
    MEDIA_NERVE = "MEDIA_NERVE"
    EMPLOYEE_TRUST = "EMPLOYEE_TRUST"
    INDUSTRY_INTEL = "INDUSTRY_INTEL"


class LegacyUnlock(BaseModel):
    """A single inherited bonus earned at the end of a run."""

    model_config = ConfigDict(frozen=True, strict=True)

    type: LegacyType
    label_zh: str = Field(max_length=12)
    description: str = Field(max_length=60)
    effect_summary: str = Field(max_length=40)
    earned_at_run_id: str
    earned_at_quarter: int = Field(ge=1, le=4)


class ManagementStyle(StrEnum):
    """Persistent management style unlocks."""

    IRON_LAYOFF = "IRON_LAYOFF"
    STORY_MASTER = "STORY_MASTER"
    DATA_FREAK = "DATA_FREAK"
    FACE_KEEPER = "FACE_KEEPER"
    SURVIVAL_PRO = "SURVIVAL_PRO"


class DeathLogEntry(BaseModel):
    """A frozen obituary snapshot for one failed or completed run."""

    model_config = ConfigDict(frozen=True, strict=True)

    run_id: str
    company_name: str
    business: str
    died_at_quarter: int = Field(ge=1, le=4)
    death_reason: DeathReason | None
    obituary: str = Field(max_length=500)
    biggest_mistake_decision_id: str | None = None
    last_employee_quote: str | None = None
    headlines: list[str] = Field(default_factory=list, max_length=3)


class MetaProgress(BaseModel):
    """Player-wide progress that survives across runs."""

    model_config = ConfigDict(strict=True)

    player_id: str = Field(default_factory=lambda: str(uuid4()))
    schema_version: int = Field(default=1, ge=1)
    unlocked_legacies: list[LegacyUnlock] = Field(default_factory=list)
    unlocked_styles: list[ManagementStyle] = Field(default_factory=list)
    death_log: list[DeathLogEntry] = Field(default_factory=list)
    press_archive: list[str] = Field(default_factory=list)
    total_runs: int = Field(default=0, ge=0)

    @field_validator("player_id")
    @classmethod
    def _validate_uuid4(cls, value: str) -> str:
        parsed = UUID(value)
        if parsed.version != 4:
            raise ValueError("player_id must be a uuid4")
        return str(parsed)

    def register_run_end(
        self,
        entry: DeathLogEntry,
        new_legacies: list[LegacyUnlock],
        new_styles: list[ManagementStyle],
    ) -> MetaProgress:
        """Return a new progress snapshot with appended run-end data."""

        unlocked_legacies = _dedupe_legacies(self.unlocked_legacies, new_legacies)
        unlocked_styles = _dedupe_styles(self.unlocked_styles, new_styles)
        return self.model_copy(
            update={
                "death_log": [*self.death_log, entry],
                "unlocked_legacies": unlocked_legacies,
                "unlocked_styles": unlocked_styles,
                "total_runs": self.total_runs + 1,
            }
        )


def _dedupe_legacies(
    current: list[LegacyUnlock],
    incoming: Iterable[LegacyUnlock],
) -> list[LegacyUnlock]:
    seen: set[LegacyType] = {unlock.type for unlock in current}
    deduped = list(current)
    for unlock in incoming:
        if unlock.type in seen:
            continue
        seen.add(unlock.type)
        deduped.append(unlock)
    return deduped


def _dedupe_styles(
    current: list[ManagementStyle],
    incoming: Iterable[ManagementStyle],
) -> list[ManagementStyle]:
    seen: set[ManagementStyle] = set(current)
    deduped = list(current)
    for style in incoming:
        if style in seen:
            continue
        seen.add(style)
        deduped.append(style)
    return deduped
