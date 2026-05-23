"""Company domain model."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from random import Random
from typing import Annotated, Any, Literal
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, field_validator

__all__ = ("Company", "DeathCause")


class DeathCause(BaseModel):
    """A named way the company can die."""

    model_config = ConfigDict(strict=True)

    category: Literal["financial", "product", "org", "market", "capital", "trust", "absurd"]
    description: str = Field(max_length=80)


class Company(BaseModel):
    """Immutable company archetype used by the simulation."""

    model_config = ConfigDict(frozen=True, strict=True)

    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str = Field(max_length=20)
    business: str = Field(max_length=30)
    absurdity: int = Field(ge=1, le=5)
    founding_motto: str = Field(max_length=30)
    death_causes: list[DeathCause] = Field(min_length=2, max_length=3)
    starting_promises: list[Annotated[str, Field(max_length=30)]] = Field(
        default_factory=list,
        max_length=3,
    )
    founded_year: int = Field(ge=2020, le=2029)

    @field_validator("id")
    @classmethod
    def _validate_uuid4(cls, value: str) -> str:
        parsed = UUID(value)
        if parsed.version != 4:
            raise ValueError("id must be a uuid4")
        return str(parsed)

    @classmethod
    def from_template(cls, template: dict[str, Any], rng_seed: int | None = None) -> Company:
        """Build a company from a template payload."""

        rng = Random(rng_seed)
        return cls(
            name=_pick_scalar(template, rng, "name", "names"),
            business=_pick_scalar(template, rng, "business", "businesses"),
            absurdity=_pick_scalar(template, rng, "absurdity"),
            founding_motto=_pick_scalar(template, rng, "founding_motto", "mottos"),
            death_causes=_pick_death_causes(template),
            starting_promises=_pick_promises(template),
            founded_year=_pick_scalar(template, rng, "founded_year", "founded_years"),
        )


def _pick_scalar(template: Mapping[str, Any], rng: Random, *keys: str) -> Any:
    for key in keys:
        if key not in template:
            continue
        value = template[key]
        if _is_non_string_sequence(value):
            values = list(value)
            if not values:
                raise ValueError(f"{key} template list cannot be empty")
            return rng.choice(values)
        return value
    raise KeyError(f"missing template field: {keys[0]}")


def _pick_death_causes(template: Mapping[str, Any]) -> list[Any]:
    raw = template["death_causes"]
    return list(raw) if _is_non_string_sequence(raw) else [raw]


def _pick_promises(template: Mapping[str, Any]) -> list[Any]:
    if "starting_promises" not in template:
        return []
    raw = template["starting_promises"]
    return list(raw) if _is_non_string_sequence(raw) else [raw]


def _is_non_string_sequence(value: Any) -> bool:
    return isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray))
