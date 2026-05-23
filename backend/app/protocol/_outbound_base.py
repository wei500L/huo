"""Shared outbound model base."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel

__all__ = ("OutboundBase",)


class OutboundBase(BaseModel):
    model_config = ConfigDict(
        strict=True,
        extra="forbid",
        frozen=True,
        populate_by_name=True,
        alias_generator=to_camel,
    )
