"""Employee, relationship, and gossip lead domain models."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from enum import StrEnum
from random import Random
from typing import Annotated, Any, Literal
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field

__all__ = (
    "Employee",
    "Faction",
    "GossipLead",
    "GossipReliability",
    "Mood",
    "PersonalityTag",
    "Relationship",
)

_MISSING = object()


def _build_employee_id() -> str:
    return f"E-{uuid4().hex[:8]}"


def _clamp_100(value: int) -> int:
    return max(0, min(100, value))


def _is_non_string_sequence(value: Any) -> bool:
    return isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray))


def _pick_scalar(
    template: Mapping[str, Any],
    rng: Random,
    *keys: str,
    default: Any = _MISSING,
) -> Any:
    for key in keys:
        if key not in template:
            continue
        value = template[key]
        if _is_non_string_sequence(value):
            options = list(value)
            if not options:
                raise ValueError(f"{key} template list cannot be empty")
            return rng.choice(options)
        return value
    if default is not _MISSING:
        return default
    raise KeyError(f"missing template field: {keys[0]}")


class PersonalityTag(StrEnum):
    GOOD_PERSON = "GOOD_PERSON"
    SLACKER = "SLACKER"
    GO_GETTER = "GO_GETTER"
    VETERAN = "VETERAN"
    TROUBLEMAKER = "TROUBLEMAKER"
    DEFECTOR = "DEFECTOR"
    IN_LOVE = "IN_LOVE"
    RADICAL = "RADICAL"
    CAUTIOUS = "CAUTIOUS"

    @property
    def label_zh(self) -> str:
        return _PERSONALITY_LABELS[self]


class Mood(StrEnum):
    HOPEFUL = "HOPEFUL"
    NEUTRAL = "NEUTRAL"
    ANXIOUS = "ANXIOUS"
    ANGRY = "ANGRY"
    NUMB = "NUMB"
    IN_LOVE = "IN_LOVE"

    @property
    def icon(self) -> str:
        return _MOOD_ICONS[self]

    @property
    def label_zh(self) -> str:
        return _MOOD_LABELS[self]


class Faction(StrEnum):
    TECH = "TECH"
    SALES = "SALES"
    FINANCE = "FINANCE"
    OPS = "OPS"
    NEUTRAL = "NEUTRAL"


class Relationship(BaseModel):
    model_config = ConfigDict(strict=True)

    target_id: str
    type: Literal[
        "close_friend",
        "crush",
        "faction_ally",
        "faction_enemy",
        "mentor",
        "rival",
    ]
    strength: int = Field(ge=0, le=100)


class Employee(BaseModel):
    model_config = ConfigDict(frozen=True, strict=True)

    id: str = Field(default_factory=_build_employee_id, pattern=r"^E-[0-9a-f]{8}$")
    name: str = Field(max_length=6)
    role: str = Field(max_length=12)
    competence: int = Field(ge=0, le=100)
    loyalty: int = Field(ge=0, le=100)
    stress: int = Field(ge=0, le=100)
    personality_tag: PersonalityTag
    faction: Faction
    relationships: list[Relationship] = Field(default_factory=list)
    # WARN: 严禁出现在 outbound 协议中
    hidden_secrets: list[Annotated[str, Field(max_length=40)]] = Field(
        default_factory=list,
        description="WARN: 严禁出现在 outbound 协议中",
    )
    attitude_to_player: int = Field(ge=0, le=100)
    current_goal: str | None = None
    mood: Mood = Mood.NEUTRAL

    def with_loyalty(self, delta: int) -> Employee:
        return self.model_copy(update={"loyalty": _clamp_100(self.loyalty + delta)})

    def with_stress(self, delta: int) -> Employee:
        return self.model_copy(update={"stress": _clamp_100(self.stress + delta)})

    def derive_mood(self) -> Mood:
        if self.loyalty > 70:
            return Mood.HOPEFUL
        if self.stress > 80 and self.loyalty < 30:
            return Mood.NUMB
        if self.loyalty < 30 and self.stress > 60:
            return Mood.ANGRY
        if self.stress > 60:
            return Mood.ANXIOUS
        if any(
            relationship.type == "crush" and relationship.strength > 50
            for relationship in self.relationships
        ):
            return Mood.IN_LOVE
        return Mood.NEUTRAL

    def is_quitting_risk(self) -> bool:
        return self.loyalty < 20 or self.attitude_to_player < 15

    @classmethod
    def from_template(cls, template: dict[str, Any], rng_seed: int | None = None) -> Employee:
        rng = Random(rng_seed)
        return cls(
            id=_pick_scalar(template, rng, default=_build_employee_id()),
            name=_pick_scalar(template, rng, "name", "names"),
            role=_pick_scalar(template, rng, "role", "roles"),
            competence=_pick_scalar(template, rng, "competence", "competences"),
            loyalty=_pick_scalar(template, rng, "loyalty", "loyalties"),
            stress=_pick_scalar(template, rng, "stress", "stresses"),
            personality_tag=PersonalityTag(
                _pick_scalar(template, rng, "personality_tag", "personality_tags")
            ),
            faction=Faction(_pick_scalar(template, rng, "faction", "factions")),
            relationships=_pick_relationships(template),
            hidden_secrets=_pick_hidden_secrets(template),
            attitude_to_player=_pick_scalar(
                template,
                rng,
                "attitude_to_player",
                "attitudes_to_player",
            ),
            current_goal=_pick_scalar(
                template,
                rng,
                "current_goal",
                "current_goals",
                default=None,
            ),
            mood=Mood(_pick_scalar(template, rng, "mood", "moods", default=Mood.NEUTRAL)),
        )


class GossipReliability(StrEnum):
    RUMOR = "RUMOR"
    LIKELY = "LIKELY"
    CONFIRMED = "CONFIRMED"

    @property
    def truth_rate(self) -> int:
        return _GOSSIP_TRUTH_RATES[self]


class GossipLead(BaseModel):
    model_config = ConfigDict(frozen=True, strict=True)

    id: str
    quarter: int = Field(ge=1, le=4)
    scene: Literal["tearoom", "elevator", "meeting_room", "workstation", "rooftop", "smoking_area"]
    speaker_id: str | None = None
    text: Annotated[str, Field(max_length=60)]
    reliability: GossipReliability
    # WARN: 禁止 outbound
    is_truth: bool = Field(description="WARN: 禁止 outbound")
    linked_employee_ids: list[str] = Field(default_factory=list)
    ap_cost: int = Field(default=1, ge=0, le=3)


_PERSONALITY_LABELS: dict[PersonalityTag, str] = {
    PersonalityTag.GOOD_PERSON: "老好人",
    PersonalityTag.SLACKER: "摸鱼",
    PersonalityTag.GO_GETTER: "卷王",
    PersonalityTag.VETERAN: "老臣",
    PersonalityTag.TROUBLEMAKER: "刺头",
    PersonalityTag.DEFECTOR: "叛逃种子",
    PersonalityTag.IN_LOVE: "恋爱中",
    PersonalityTag.RADICAL: "革命派",
    PersonalityTag.CAUTIOUS: "谨慎",
}

_MOOD_ICONS: dict[Mood, str] = {
    Mood.HOPEFUL: "💡",
    Mood.NEUTRAL: "⚪",
    Mood.ANXIOUS: "💧",
    Mood.ANGRY: "🔥",
    Mood.NUMB: "⚫",
    Mood.IN_LOVE: "💗",
}

_MOOD_LABELS: dict[Mood, str] = {
    Mood.HOPEFUL: "充满希望",
    Mood.NEUTRAL: "中立",
    Mood.ANXIOUS: "焦虑",
    Mood.ANGRY: "愤怒",
    Mood.NUMB: "麻木",
    Mood.IN_LOVE: "恋爱中",
}

_GOSSIP_TRUTH_RATES: dict[GossipReliability, int] = {
    GossipReliability.RUMOR: 30,
    GossipReliability.LIKELY: 50,
    GossipReliability.CONFIRMED: 90,
}


def _pick_relationships(template: Mapping[str, Any]) -> list[Relationship]:
    raw = template.get("relationships", template.get("relationships_seed", []))
    if raw is None:
        return []
    if _is_non_string_sequence(raw):
        return [Relationship.model_validate(item) for item in raw]
    return [Relationship.model_validate(raw)]


def _pick_hidden_secrets(template: Mapping[str, Any]) -> list[str]:
    raw = template.get("hidden_secrets", [])
    if raw is None:
        return []
    if _is_non_string_sequence(raw):
        return list(raw)
    return [raw]
