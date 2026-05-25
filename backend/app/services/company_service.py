"""Company bootstrap service."""

from __future__ import annotations

from collections.abc import Callable
from datetime import datetime, timedelta
from random import Random
from typing import Any, Literal, cast
from uuid import UUID

import app.content as content_registry
from app.domain import (
    Briefing,
    Company,
    DeathCause,
    Employee,
    Faction,
    LegacyType,
    LegacyUnlock,
    MetaProgress,
    Mood,
    PersonalityTag,
    Quarter,
    QuarterPhase,
    Relationship,
    Stats,
    StatsDelta,
)
from app.repo.protocols import GameSession, GameSessionRepo, MetaProgressRepo

__all__ = ("CompanyService",)

MarketMood = Literal["bull", "neutral", "bear", "crisis"]
_SESSION_START = datetime(2026, 5, 23, 9, 0, 0)
sample_company_template = content_registry.sample_company_template
get_company_template_by_id = content_registry.get_company_template_by_id
sample_employee_set = content_registry.sample_employee_set


class CompanyService:
    """Create a fresh run from registry templates."""

    def __init__(
        self,
        session_repo: GameSessionRepo,
        meta_repo: MetaProgressRepo,
        rng_factory: Callable[[int | None], Random] = Random,
    ) -> None:
        self.session_repo = session_repo
        self.meta_repo = meta_repo
        self.rng_factory = rng_factory

    async def create_new_run(
        self,
        player_id: str | None = None,
        apply_legacies: bool = True,
        rng_seed: int | None = None,
        company_template_id: str | None = None,
    ) -> GameSession:
        rng = self.rng_factory(rng_seed)
        if player_id is None:
            player_id = _uuid4_str(rng)

        try:
            company_template = (
                get_company_template_by_id(company_template_id)
                if company_template_id is not None
                else sample_company_template(rng.randrange(2**32))
            )
            if company_template is None:
                raise content_registry.ContentRegistryError(
                    f"unknown company template: {company_template_id}"
                )
            employee_templates = sample_employee_set(rng.randrange(2**32))
            company = _build_company(company_template, rng)
            employees = _build_employees(employee_templates, rng)
        except Exception as exc:  # noqa: BLE001 - translate registry failures
            raise content_registry.ContentRegistryError("failed to build run content") from exc

        meta = await self.meta_repo.get(player_id)
        await self.meta_repo.save(meta)
        stats = _compute_initial_stats(
            company_template=company_template,
            meta=meta,
            apply_legacies=apply_legacies,
            rng=rng,
        )
        briefing = _make_briefing(1, company, rng)
        created_at = _build_timestamp(rng)
        session = GameSession(
            id=_uuid4_str(rng),
            player_id=player_id,
            company=company,
            stats=stats,
            quarter=Quarter(number=1, phase=QuarterPhase.BRIEFING, briefing=briefing),
            employees=employees,
            created_at=created_at,
            updated_at=created_at,
        )
        return await self.session_repo.create(session)


def _build_company(template: dict[str, Any], rng: Random) -> Company:
    try:
        name_pool = list(template["name_pool"])
        death_causes = list(template["death_causes"])
        starting_promises = list(template["starting_promises"])
    except KeyError as exc:  # pragma: no cover - content registry contract
        message = f"missing company field: {exc.args[0]}"
        raise content_registry.ContentRegistryError(message) from exc
    if not name_pool:
        raise content_registry.ContentRegistryError("company name pool cannot be empty")
    return Company(
        id=_uuid4_str(rng),
        name=rng.choice(name_pool),
        business=str(template["business"]),
        absurdity=int(template["absurdity"]),
        founding_motto=str(template["founding_motto"]),
        death_causes=[DeathCause(**cause) for cause in death_causes],
        starting_promises=[str(promise) for promise in starting_promises],
        founded_year=int(template["founded_year"]),
    )


def _build_employees(templates: list[dict[str, Any]], rng: Random) -> list[Employee]:
    employees: list[Employee] = []
    for template in templates:
        competence = _sample_range(template, "competence_range", rng)
        loyalty = _sample_range(template, "loyalty_range", rng)
        stress = _sample_range(template, "stress_range", rng)
        employee = Employee(
            id=_employee_id_from_rng(rng),
            name=_sample_name(template, rng),
            role=str(template["role"]),
            competence=competence,
            loyalty=loyalty,
            stress=stress,
            personality_tag=PersonalityTag(str(template["personality_tag"])),
            faction=Faction(str(template["faction"])),
            relationships=[],
            hidden_secrets=_sample_hidden_secrets(template, rng),
            attitude_to_player=_sample_attitude(loyalty, rng),
            current_goal=None,
            mood=_derive_mood(loyalty=loyalty, stress=stress),
        )
        employees.append(employee)
    return _resolve_relationships(employees, templates)


def _resolve_relationships(
    employees: list[Employee],
    templates: list[dict[str, Any]],
) -> list[Employee]:
    template_to_id = {
        str(template["template_id"]): employee.id
        for employee, template in zip(employees, templates, strict=True)
    }
    resolved: list[Employee] = []
    for employee, template in zip(employees, templates, strict=True):
        relationships = [
            Relationship(
                target_id=_resolve_target_id(seed, template_to_id),
                type=str(seed["type"]),  # type: ignore[arg-type]
                strength=int(seed["strength"]),
            )
            for seed in template.get("relationships_seed", [])
        ]
        resolved.append(employee.model_copy(update={"relationships": relationships}))
    return resolved


def _resolve_target_id(seed: dict[str, Any], template_to_id: dict[str, str]) -> str:
    target_template_id = str(seed.get("target_template_id") or seed.get("template_id") or "")
    if target_template_id not in template_to_id:
        raise content_registry.ContentRegistryError(
            f"unknown relationship target template: {target_template_id}"
        )
    return template_to_id[target_template_id]


def _compute_initial_stats(
    company_template: dict[str, Any],
    meta: MetaProgress,
    apply_legacies: bool,
    rng: Random,
) -> Stats:
    stats = Stats.starting(seed=rng.randrange(2**32))
    stats = stats.apply_delta(StatsDelta(**company_template["stats_modifiers"]))
    if apply_legacies:
        stats = _apply_legacy_buffs(stats, meta.unlocked_legacies)
    return stats


def _apply_legacy_buffs(stats: Stats, legacy_unlocks: list[LegacyUnlock]) -> Stats:
    for unlock in legacy_unlocks:
        stats = stats.apply_delta(_legacy_delta(unlock.type))
    return stats


def _legacy_delta(legacy_type: LegacyType) -> StatsDelta:
    return {
        LegacyType.PR_EXPERIENCE: StatsDelta(FACE=5),
        LegacyType.FUNDING_PITCH: StatsDelta(BOARD=3),
        LegacyType.ORG_KNOWHOW: StatsDelta(MORALE=5),
        LegacyType.PRODUCT_TASTE: StatsDelta(BOARD=4),
        LegacyType.MEDIA_NERVE: StatsDelta(FACE=5),
        LegacyType.EMPLOYEE_TRUST: StatsDelta(MORALE=4),
        LegacyType.INDUSTRY_INTEL: StatsDelta(BOARD=4),
    }[legacy_type]


def _make_briefing(quarter: int, company: Company, rng: Random) -> Briefing:
    market_mood = cast(
        MarketMood,
        rng.choices(
            population=["bull", "neutral", "bear", "crisis"],
            weights=[0.25, 0.4, 0.25, 0.1],
            k=1,
        )[0],
    )
    return Briefing(
        quarter=quarter,
        market_mood=market_mood,
        headline_hint=_headline_hint(company, market_mood),
        hidden_risks=_hidden_risks(company, rng, market_mood),
    )


def _headline_hint(company: Company, market_mood: MarketMood) -> str:
    templates = {
        "bull": f"{company.business} 正在借势抬头",
        "neutral": f"{company.business} 还在试探市场边界",
        "bear": f"{company.business} 先守住现金再谈扩张",
        "crisis": f"{company.business} 正被现金和舆论同时盯上",
    }
    return templates[market_mood]


def _hidden_risks(company: Company, rng: Random, market_mood: MarketMood) -> list[str]:
    risks = [f"{cause.category}: {cause.description}" for cause in company.death_causes]
    count = min(2, len(risks)) if market_mood in {"crisis", "bear"} else 1
    return rng.sample(risks, count) if risks else []


def _sample_name(template: dict[str, Any], rng: Random) -> str:
    names = list(template["name_pool"])
    if not names:
        raise content_registry.ContentRegistryError("employee name pool cannot be empty")
    return str(rng.choice(names))


def _sample_range(template: dict[str, Any], field: str, rng: Random) -> int:
    bounds = list(template[field])
    if len(bounds) != 2:
        raise content_registry.ContentRegistryError(f"{field} must contain exactly two ints")
    return rng.randint(int(bounds[0]), int(bounds[1]))


def _sample_hidden_secrets(template: dict[str, Any], rng: Random) -> list[str]:
    pool = [str(item) for item in template.get("hidden_secrets_pool", [])]
    if not pool:
        return []
    count = rng.randint(0, min(2, len(pool)))
    return rng.sample(pool, count)


def _sample_attitude(loyalty: int, rng: Random) -> int:
    return max(0, min(100, loyalty + rng.randint(-10, 10)))


def _derive_mood(loyalty: int, stress: int) -> Mood:
    if loyalty > 70:
        return Mood.HOPEFUL
    if stress > 80 and loyalty < 30:
        return Mood.NUMB
    if loyalty < 30 and stress > 60:
        return Mood.ANGRY
    if stress > 60:
        return Mood.ANXIOUS
    return Mood.NEUTRAL


def _employee_id_from_rng(rng: Random) -> str:
    return f"E-{_uuid4_from_rng(rng).hex[:8]}"


def _build_timestamp(rng: Random) -> datetime:
    return _SESSION_START + timedelta(minutes=rng.randrange(0, 24 * 60))


def _uuid4_str(rng: Random) -> str:
    return str(_uuid4_from_rng(rng))


def _uuid4_from_rng(rng: Random) -> UUID:
    bits = rng.getrandbits(128)
    bits &= ~(0xF << 76)
    bits |= 0x4 << 76
    bits &= ~(0x3 << 62)
    bits |= 0x2 << 62
    return UUID(int=bits)
