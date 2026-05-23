"""Tests for the quarter domain models."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.domain import Briefing, HistoryEntry, Quarter, QuarterPhase, Stats


def test_quarter_defaults_to_briefing_phase() -> None:
    quarter = Quarter(number=1)

    assert quarter.phase == QuarterPhase.BRIEFING


def test_quarter_rejects_negative_ap_remaining() -> None:
    with pytest.raises(ValidationError):
        Quarter(number=1, ap_remaining=-1)


def test_briefing_hidden_risks_field_warns_outbound_consumers() -> None:
    description = Briefing.model_fields["hidden_risks"].description

    assert description is not None
    assert "WARN" in description


def test_history_entry_is_frozen_and_uses_stats_snapshots() -> None:
    entry = HistoryEntry(
        quarter=1,
        decision_id="D_LAYOFF_01",
        stats_before=Stats(CASH=50, MORALE=50, BOARD=50, FACE=60),
        stats_after=Stats(CASH=46, MORALE=47, BOARD=49, FACE=55),
        settlement_summary="现金流暂时止血，但舆论仍在继续发酵。",
    )

    assert entry.stats_before == Stats(CASH=50, MORALE=50, BOARD=50, FACE=60)
    assert entry.stats_after == Stats(CASH=46, MORALE=47, BOARD=49, FACE=55)

    with pytest.raises(ValidationError):
        entry.quarter = 2
