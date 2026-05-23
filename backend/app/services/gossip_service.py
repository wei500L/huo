"""Gossip collection service for the real-time phase."""

from __future__ import annotations

import random
from collections.abc import Callable
from typing import Any, Literal, cast
from uuid import UUID

from app.content import sample_gossip_lead
from app.domain import Employee, GossipLead, GossipReliability, QuarterPhase
from app.repo.protocols import GameSession, GameSessionRepo

__all__ = (
    "GossipService",
    "GossipServiceError",
    "InsufficientAP",
    "InvalidPhaseForGossip",
    "InvalidScene",
)

_ALLOWED_SCENES = {
    "tearoom",
    "elevator",
    "meeting_room",
    "workstation",
    "rooftop",
    "smoking_area",
}
_ALLOWED_PHASES = {QuarterPhase.BRIEFING, QuarterPhase.GOSSIP}
GossipScene = Literal[
    "tearoom",
    "elevator",
    "meeting_room",
    "workstation",
    "rooftop",
    "smoking_area",
]


class GossipServiceError(Exception):
    """Base error for gossip collection failures."""


class InsufficientAP(GossipServiceError):
    """Raised when the session does not have enough AP for gossip."""


class InvalidScene(GossipServiceError):
    """Raised when a scene is not part of the gossip whitelist."""


class InvalidPhaseForGossip(GossipServiceError):
    """Raised when gossip is requested outside of the allowed phases."""


class GossipService:
    """Owns gossip sampling, AP consumption, and lead persistence."""

    def __init__(
        self,
        session_repo: GameSessionRepo,
        rng_factory: Callable[[int | None], random.Random] = random.Random,
    ) -> None:
        self.session_repo = session_repo
        self.rng_factory = rng_factory

    async def collect_gossip(
        self,
        session_id: str,
        scene: str,
        rng_seed: int | None = None,
    ) -> GossipLead:
        session = await self._load_session(session_id)
        self._validate_phase(session)
        self._validate_scene(scene)

        available_ap = session.quarter.ap_remaining
        if available_ap < 1:
            raise InsufficientAP(f"not enough AP: have {available_ap}, need at least 1")

        rng = self.rng_factory(rng_seed)
        payload = sample_gossip_lead(scene, session.employees, rng)
        lead = self._build_lead(session, scene, payload, rng)

        if available_ap < lead.ap_cost:
            raise InsufficientAP(
                f"not enough AP: have {available_ap}, need {lead.ap_cost}",
            )

        quarter = session.quarter.model_copy(
            update={
                "gossip_collected": [*session.quarter.gossip_collected, lead.id],
                "collected_leads": [*session.quarter.collected_leads, lead],
                "ap_remaining": available_ap - lead.ap_cost,
            },
        )
        updated = session.model_copy(update={"quarter": quarter})
        await self.session_repo.save(updated)
        return lead

    async def get_collected_leads(self, session_id: str) -> list[GossipLead]:
        session = await self._load_session(session_id)
        lead_by_id = {lead.id: lead for lead in session.quarter.collected_leads}
        return [
            lead_by_id[lead_id].model_copy(deep=True)
            for lead_id in session.quarter.gossip_collected
            if lead_id in lead_by_id
        ]

    async def _load_session(self, session_id: str) -> GameSession:
        session = await self.session_repo.get(session_id)
        if session is None:
            raise GossipServiceError(f"session not found: {session_id}")
        return session

    def _validate_phase(self, session: GameSession) -> None:
        if session.quarter.phase not in _ALLOWED_PHASES:
            raise InvalidPhaseForGossip(f"cannot collect gossip from {session.quarter.phase}")

    def _validate_scene(self, scene: str) -> None:
        if scene not in _ALLOWED_SCENES:
            raise InvalidScene(f"unknown gossip scene: {scene}")

    def _build_lead(
        self,
        session: GameSession,
        scene: str,
        payload: dict[str, Any],
        rng: random.Random,
    ) -> GossipLead:
        speaker_id = cast(str | None, payload.get("speaker_id"))
        linked_ids = payload.get("linked_employee_ids")
        if isinstance(linked_ids, list) and linked_ids:
            linked_employee_ids = [str(employee_id) for employee_id in linked_ids]
        else:
            linked_employee_ids = _linked_employee_ids_from_tags(
                session.employees,
                cast(object, payload.get("linked_role_tags")),
                speaker_id,
            )

        return GossipLead(
            id=f"G-{UUID(int=rng.getrandbits(128))}",
            quarter=session.quarter.number,
            scene=cast(GossipScene, str(payload.get("scene", scene))),
            speaker_id=None if speaker_id is None else str(speaker_id),
            text=str(cast(Any, payload["text"])),
            reliability=GossipReliability(cast(str, payload["reliability"])),
            is_truth=bool(cast(Any, payload["is_truth"])),
            linked_employee_ids=linked_employee_ids,
            ap_cost=int(cast(Any, payload.get("ap_cost", 1))),
        )


def _linked_employee_ids_from_tags(
    employees: list[Employee],
    linked_role_tags: object,
    speaker_id: str | None,
) -> list[str]:
    if isinstance(linked_role_tags, (list, tuple, set)):
        tags = {str(tag).upper() for tag in linked_role_tags}
    else:
        tags = set()
    linked_ids = [
        employee.id
        for employee in employees
        if tags and any(tag in employee.role.upper() for tag in tags)
    ]
    if linked_ids:
        return linked_ids
    if speaker_id is None:
        return []
    return [str(speaker_id)]
