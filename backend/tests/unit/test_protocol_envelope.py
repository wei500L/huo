"""Tests for protocol envelopes."""

from __future__ import annotations

from uuid import UUID

from app.protocol import CreateGame, Envelope, MessageDirection


def test_envelope_wrap_auto_fills_type() -> None:
    message = CreateGame(player_id=None, request_legacies=False)

    envelope = Envelope.wrap(MessageDirection.INBOUND, message)

    assert envelope.v == 1
    assert UUID(envelope.id).version == 4
    assert envelope.direction == MessageDirection.INBOUND
    assert envelope.type == "create_game"
    assert envelope.ack_for is None
    assert envelope.payload == message


def test_envelope_generic_round_trip() -> None:
    envelope = Envelope[CreateGame](
        direction=MessageDirection.OUTBOUND,
        type="create_game",
        payload=CreateGame(player_id="P-0001", request_legacies=True),
    )

    round_tripped = Envelope[CreateGame].model_validate_json(envelope.model_dump_json())

    assert round_tripped == envelope


def test_envelope_ack_for_is_optional() -> None:
    envelope = Envelope[CreateGame](
        direction=MessageDirection.OUTBOUND,
        type="create_game",
        ack_for="inbound-123",
        payload=CreateGame(),
    )

    assert envelope.ack_for == "inbound-123"
