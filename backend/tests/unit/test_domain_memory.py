"""Tests for the memory domain model."""

from __future__ import annotations

import pytest

from app.domain import MemoryActor, MemoryWindow, ScheduledEvent
from tests.factories import build_agent_memory, build_scheduled_event


def test_memory_window_append_sorts_and_truncates() -> None:
    window = MemoryWindow(entries=[], max_size=6)
    entries = [
        build_agent_memory(id="M-01", quarter=1, weight=1),
        build_agent_memory(id="M-02", quarter=4, weight=2),
        build_agent_memory(id="M-03", quarter=3, weight=5),
        build_agent_memory(id="M-04", quarter=4, weight=5),
        build_agent_memory(id="M-05", quarter=2, weight=4),
        build_agent_memory(id="M-06", quarter=3, weight=2),
        build_agent_memory(id="M-07", quarter=4, weight=1),
        build_agent_memory(id="M-08", quarter=2, weight=5),
        build_agent_memory(id="M-09", quarter=1, weight=5),
        build_agent_memory(id="M-10", quarter=3, weight=4),
    ]

    for entry in entries:
        window = window.append(entry)

    expected = sorted(entries, key=lambda item: (item.quarter, item.weight), reverse=True)[:6]

    assert len(window.entries) == 6
    assert window.entries == expected


def test_scheduled_event_resolved_defaults_false() -> None:
    event = build_scheduled_event()

    assert isinstance(event, ScheduledEvent)
    assert event.resolved is False


@pytest.mark.parametrize(
    "actor",
    [
        MemoryActor.BOARD,
        MemoryActor.EMPLOYEE,
        MemoryActor.MEDIA,
        MemoryActor.RIVAL,
    ],
)
def test_memory_actor_members(actor: MemoryActor) -> None:
    entry = build_agent_memory(actor=actor)

    assert entry.actor is actor
