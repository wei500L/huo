"""Unit tests for GossipService."""

from __future__ import annotations

from collections import Counter
from datetime import UTC, datetime
from random import Random
from typing import Any

import pytest

from app.domain import MemoryWindow, QuarterPhase
from app.repo.memory_impl import InMemoryGameSessionRepo
from app.repo.protocols import GameSession
from app.services.gossip_service import (
    GossipService,
    InsufficientAP,
    InvalidPhaseForGossip,
    InvalidScene,
)
from tests.factories import build_company, build_employee, build_quarter, build_stats


@pytest.mark.asyncio
async def test_collect_gossip_persists_lead_and_consumes_ap() -> None:
    repo = InMemoryGameSessionRepo()
    service = GossipService(session_repo=repo)
    session = await repo.create(_build_session(ap_remaining=3))
    original_employees = [employee.model_copy(deep=True) for employee in session.employees]

    lead = await service.collect_gossip(session.id, "tearoom", rng_seed=11)

    persisted = await repo.get(session.id)
    assert persisted is not None
    assert persisted.quarter.ap_remaining == 2
    assert persisted.quarter.gossip_collected == [lead.id]
    assert len(persisted.quarter.collected_leads) == 1
    assert persisted.quarter.collected_leads[0] == lead
    assert persisted.employees == original_employees

    collected = await service.get_collected_leads(session.id)
    assert collected == [lead]


@pytest.mark.asyncio
async def test_collect_gossip_rejects_zero_ap() -> None:
    repo = InMemoryGameSessionRepo()
    service = GossipService(session_repo=repo)
    session = await repo.create(_build_session(ap_remaining=0))

    with pytest.raises(InsufficientAP):
        await service.collect_gossip(session.id, "tearoom", rng_seed=1)


@pytest.mark.asyncio
async def test_collect_gossip_rejects_invalid_scene() -> None:
    repo = InMemoryGameSessionRepo()
    service = GossipService(session_repo=repo)
    session = await repo.create(_build_session())

    with pytest.raises(InvalidScene):
        await service.collect_gossip(session.id, "xxx", rng_seed=1)


@pytest.mark.asyncio
async def test_collect_gossip_rejects_decision_phase() -> None:
    repo = InMemoryGameSessionRepo()
    service = GossipService(session_repo=repo)
    session = await repo.create(_build_session(phase=QuarterPhase.DECISION))

    with pytest.raises(InvalidPhaseForGossip):
        await service.collect_gossip(session.id, "tearoom", rng_seed=1)


@pytest.mark.asyncio
async def test_collect_gossip_allows_briefing_phase() -> None:
    repo = InMemoryGameSessionRepo()
    service = GossipService(session_repo=repo)
    session = await repo.create(_build_session(phase=QuarterPhase.BRIEFING, ap_remaining=2))

    lead = await service.collect_gossip(session.id, "tearoom", rng_seed=7)

    persisted = await repo.get(session.id)
    assert persisted is not None
    assert persisted.quarter.ap_remaining == 1
    assert persisted.quarter.collected_leads[0] == lead


@pytest.mark.asyncio
async def test_same_rng_seed_repeats_collect_output(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr("app.services.gossip_service.sample_gossip_lead", _fake_sample_gossip_lead)

    first_repo = InMemoryGameSessionRepo()
    second_repo = InMemoryGameSessionRepo()
    first_session = await first_repo.create(_build_session(session_id="S-first"))
    second_session = await second_repo.create(_build_session(session_id="S-second"))

    first_lead = await GossipService(first_repo).collect_gossip(
        first_session.id,
        "tearoom",
        rng_seed=99,
    )
    second_lead = await GossipService(second_repo).collect_gossip(
        second_session.id,
        "tearoom",
        rng_seed=99,
    )

    assert first_lead == second_lead


@pytest.mark.asyncio
async def test_truth_probability_half_stays_in_range(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "app.services.gossip_service.sample_gossip_lead",
        _fake_sample_gossip_lead_factory(truth_probability=0.5),
    )

    repo = InMemoryGameSessionRepo()
    session = await repo.create(_build_session(ap_remaining=2000))
    service = GossipService(repo)

    truths = 0
    for seed in range(1000):
        lead = await service.collect_gossip(session.id, "tearoom", rng_seed=seed)
        truths += int(lead.is_truth)

    ratio = truths / 1000
    assert 0.45 <= ratio <= 0.55


@pytest.mark.asyncio
async def test_reliability_distribution_matches_template_weights(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    distribution = {"RUMOR": 0.3, "LIKELY": 0.5, "CONFIRMED": 0.2}
    monkeypatch.setattr(
        "app.services.gossip_service.sample_gossip_lead",
        _fake_sample_gossip_lead_factory(
            truth_probability=0.5,
            reliability_distribution=distribution,
        ),
    )

    repo = InMemoryGameSessionRepo()
    session = await repo.create(_build_session(ap_remaining=2000))
    service = GossipService(repo)

    counts: Counter[str] = Counter()
    for seed in range(1000):
        lead = await service.collect_gossip(session.id, "tearoom", rng_seed=seed)
        counts[lead.reliability.value] += 1

    total = sum(counts.values())
    for key, expected in distribution.items():
        assert abs((counts[key] / total) - expected) < 0.05


def _build_session(
    *,
    session_id: str = "S-gossip",
    phase: QuarterPhase = QuarterPhase.GOSSIP,
    ap_remaining: int = 10,
) -> GameSession:
    now = datetime.now(UTC)
    employees = [
        build_employee(id="E-00000001", name="陈砚", role="CFO"),
        build_employee(id="E-00000002", name="唐婉", role="HR"),
        build_employee(id="E-00000003", name="沈知远", role="CTO"),
    ]
    return GameSession(
        id=session_id,
        player_id="player-1",
        company=build_company(),
        stats=build_stats(),
        quarter=build_quarter(phase=phase, ap_remaining=ap_remaining),
        employees=employees,
        history=[],
        promise_log=[],
        agent_memory=MemoryWindow(entries=[]),
        scheduled_events=[],
        status="active",
        created_at=now,
        updated_at=now,
    )


def _fake_sample_gossip_lead(
    scene: str,
    employees: list[Any],
    rng: Random,
) -> dict[str, object]:
    return _fake_sample_gossip_lead_factory()(scene, employees, rng)


def _fake_sample_gossip_lead_factory(
    *,
    truth_probability: float = 0.5,
    reliability_distribution: dict[str, float] | None = None,
):
    distribution = reliability_distribution or {
        "RUMOR": 0.3,
        "LIKELY": 0.5,
        "CONFIRMED": 0.2,
    }
    labels = list(distribution)
    weights = list(distribution.values())

    def _sample(scene: str, employees: list[Any], rng: Random) -> dict[str, object]:
        speaker = employees[rng.randrange(len(employees))]
        reliability = rng.choices(labels, weights=weights, k=1)[0]
        return {
            "scene": scene,
            "speaker_id": speaker.id,
            "linked_employee_ids": [speaker.id],
            "text": f"{scene}:{speaker.name}:{reliability}",
            "reliability": reliability,
            "is_truth": rng.random() < truth_probability,
            "ap_cost": 1,
        }

    return _sample
