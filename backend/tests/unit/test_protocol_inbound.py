"""Tests for inbound protocol messages."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest
from pydantic import TypeAdapter, ValidationError

from app.protocol import CollectGossip, InboundMessage, SelectDecision, SubmitPress


@pytest.mark.parametrize(
    ("transcript", "should_pass"),
    [
        ("a" * 29, False),
        ("a" * 30, True),
        ("a" * 600, True),
        ("a" * 601, False),
    ],
)
def test_submit_press_transcript_length_bounds(transcript: str, should_pass: bool) -> None:
    payload = {
        "session_id": "S-0001",
        "press_type": "CRISIS",
        "transcript": transcript,
        "duration_s": 91.5,
    }

    if should_pass:
        message = SubmitPress(**payload)
        assert len(message.transcript) == len(transcript)
        assert message.quarter_number == 3
    else:
        with pytest.raises(ValidationError):
            SubmitPress(**payload)


def test_collect_gossip_scene_rejects_unknown_value() -> None:
    with pytest.raises(ValidationError):
        CollectGossip(
            session_id="S-0001",
            quarter_number=2,
            scene="lobby",  # type: ignore[arg-type]
        )


def test_inbound_message_discriminated_union_routes_by_type() -> None:
    adapter = TypeAdapter(InboundMessage)

    message = adapter.validate_python(
        {
            "type": "select_decision",
            "session_id": "S-0001",
            "quarter_number": 2,
            "card_id": "D_LAYOFF_01",
        }
    )

    assert isinstance(message, SelectDecision)
    assert message.session_id == "S-0001"
    assert message.card_id == "D_LAYOFF_01"


def test_ping_accepts_timestamp() -> None:
    adapter = TypeAdapter(InboundMessage)
    message = adapter.validate_python(
        {
            "type": "ping",
            "sent_at": datetime(2026, 5, 23, 9, 0, tzinfo=UTC),
        }
    )

    assert message.type == "ping"
