"""Tests for press type content templates."""

from __future__ import annotations

from app.content import (
    PRESS_TYPES,
    get_default_press_for_quarter,
    get_press_type_by_id,
    list_press_types,
)


def test_press_type_registry_is_complete() -> None:
    assert len(PRESS_TYPES) == 8
    assert len(list_press_types()) == 8
    assert get_press_type_by_id("CRISIS") is not None


def test_default_press_for_quarter_is_v1_strict() -> None:
    assert get_default_press_for_quarter(3) == "CRISIS"
    assert get_default_press_for_quarter(2) is None
