"""Tests for the press domain models."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.domain import MediaHeadline, PressEvaluation
from tests.factories import build_press_evaluation, build_press_input


@pytest.mark.parametrize(
    ("transcript", "should_pass"),
    [
        ("a" * 29, False),
        ("a" * 30, True),
        ("a" * 600, True),
        ("a" * 601, False),
    ],
)
def test_press_input_transcript_length_bounds(transcript: str, should_pass: bool) -> None:
    if should_pass:
        model = build_press_input(transcript=transcript, word_count=len(transcript))
        assert len(model.transcript) == len(transcript)
    else:
        with pytest.raises(ValidationError):
            build_press_input(transcript=transcript, word_count=len(transcript))


def test_media_headline_rejects_unknown_outlet() -> None:
    with pytest.raises(ValidationError):
        MediaHeadline(
            outlet="未收录媒体",
            headline="这条标题足够短",
            tone="neutral",
        )


def test_press_evaluation_scores_require_all_nine_keys() -> None:
    payload = build_press_evaluation().model_dump()
    payload["scores"].pop("authenticity")

    with pytest.raises(ValidationError):
        PressEvaluation(**payload)
