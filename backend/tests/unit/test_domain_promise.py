"""Tests for the promise domain model."""

from __future__ import annotations

import pytest

from app.domain import Promise, PromiseSource
from tests.factories import build_promise


def test_promise_parsed_none_is_valid() -> None:
    promise = build_promise(parsed=None)

    assert isinstance(promise, Promise)
    assert promise.parsed is None


@pytest.mark.parametrize("fulfilled", [None, True, False])
def test_promise_fulfilled_three_states_are_valid(fulfilled: bool | None) -> None:
    promise = build_promise(fulfilled=fulfilled)

    assert promise.fulfilled is fulfilled


@pytest.mark.parametrize(
    "source",
    [
        PromiseSource.PRESS,
        PromiseSource.BOARD_QA,
        PromiseSource.DECISION_FLAVOR,
        PromiseSource.FREE_TEXT,
    ],
)
def test_promise_source_members(source: PromiseSource) -> None:
    promise = build_promise(source=source)

    assert promise.source is source
