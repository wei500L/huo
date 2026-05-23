"""Extra coverage for domain models used by the factory and protocol layers."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from app.domain import (
    Company,
    DeathCause,
    Employee,
    Faction,
    MediaHeadline,
    Mood,
    PersonalityTag,
    PressBundle,
    PressEvaluation,
    PressInput,
    PressType,
    Relationship,
    StatsDelta,
)


def test_employee_template_and_state_transitions() -> None:
    employee = Employee.from_template(
        {
            "id": "E-abcdef12",
            "names": ["张三", "李四"],
            "roles": ["后端工程师", "测试负责人"],
            "competence": [70, 80],
            "loyalty": [25, 85],
            "stress": [20, 90],
            "personality_tags": [PersonalityTag.GOOD_PERSON.value],
            "factions": [Faction.TECH.value],
            "relationships": [
                {"target_id": "E-11111111", "type": "crush", "strength": 80},
            ],
            "hidden_secrets": ["旧账"],
            "attitudes_to_player": [18, 44],
            "current_goals": ["修复缺陷"],
            "moods": [Mood.NEUTRAL.value],
        },
        rng_seed=7,
    )

    assert employee.id.startswith("E-")
    assert employee.name in {"张三", "李四"}
    assert employee.relationships[0].type == "crush"
    assert employee.hidden_secrets == ["旧账"]
    assert employee.current_goal == "修复缺陷"

    hopeful = employee.model_copy(update={"loyalty": 80, "stress": 10})
    anxious = employee.model_copy(update={"loyalty": 40, "stress": 70})
    angry = employee.model_copy(update={"loyalty": 20, "stress": 65})
    numb = employee.model_copy(update={"loyalty": 10, "stress": 90})
    in_love = employee.model_copy(
        update={
            "loyalty": 40,
            "stress": 10,
            "relationships": [
                Relationship(target_id="E-22222222", type="crush", strength=90),
            ],
        }
    )

    assert hopeful.derive_mood() == Mood.HOPEFUL
    assert anxious.derive_mood() == Mood.ANXIOUS
    assert angry.derive_mood() == Mood.ANGRY
    assert numb.derive_mood() == Mood.NUMB
    assert in_love.derive_mood() == Mood.IN_LOVE
    assert employee.with_loyalty(-999).loyalty == 0
    assert employee.with_stress(999).stress == 100
    assert employee.model_copy(update={"loyalty": 10}).is_quitting_risk() is True


def test_press_models_validate_and_roundtrip() -> None:
    press_input = PressInput(
        quarter=3,
        press_type=PressType.CRISIS,
        must_answer_topics=["现金流"],
        transcript=(
            "我们会持续回应市场关切，并把现金流、组织和产品节奏说清楚，"
            "同时给出明确的推进顺序、责任人和沟通节奏。"
        ),
        duration_s=90.0,
        word_count=88,
        submitted_at=datetime(2026, 5, 23, 9, 0, tzinfo=UTC),
    )
    evaluation = PressEvaluation.model_validate(
        {
            "scores": {
                "contentCompleteness": 70,
                "issueResponse": 68,
                "overpromise": 20,
                "logicClarity": 61,
                "confidence": 55,
                "riskAvoidance": 50,
                "memorableQuote": 79,
                "weaknessExposed": 62,
                "authenticity": 64,
            },
            "memorable_quote": "我们把问题摊开说。",
            "biggest_flaw": "时间表不够明确",
            "media_angle": "漏洞放大",
            "stat_impact": StatsDelta(CASH=-2, MORALE=-3, BOARD=1, FACE=-1),
        }
    )
    bundle = PressBundle(
        input=press_input,
        evaluation=evaluation,
        headlines=[MediaHeadline(outlet="晚点 LatePost", headline="公司回应危机", tone="neutral")],
    )

    assert press_input.press_type.label_zh == "危机回应"
    assert PressType.INAUGURATION.label_zh == "就职"
    assert PressType.PRODUCT.label_zh == "产品发布"
    assert PressType.FINANCIAL.label_zh == "财务说明"
    assert PressType.ROADSHOW.label_zh == "路演"
    assert PressType.LAYOFF_EXPLAIN.label_zh == "裁员说明"
    assert PressType.REGULATOR.label_zh == "监管沟通"
    assert PressType.COUNTER.label_zh == "反击回应"
    assert bundle.headlines[0].summary is None

    with pytest.raises(ValidationError):
        PressEvaluation.model_validate(
            {
                "scores": {
                    "contentCompleteness": 70,
                    "issueResponse": 68,
                    "overpromise": 20,
                    "logicClarity": 61,
                    "confidence": 55,
                    "riskAvoidance": 50,
                    "memorableQuote": 79,
                    "weaknessExposed": 62,
                },
                "memorable_quote": "我们把问题摊开说。",
                "biggest_flaw": "时间表不够明确",
                "media_angle": "漏洞放大",
                "stat_impact": StatsDelta(CASH=-2, MORALE=-3, BOARD=1, FACE=-1),
            }
        )

    with pytest.raises(ValidationError):
        PressEvaluation.model_validate(
            {
                "scores": {
                    "contentCompleteness": 70,
                    "issueResponse": 68,
                    "overpromise": 20,
                    "logicClarity": 61,
                    "confidence": 55,
                    "riskAvoidance": 50,
                    "memorableQuote": 79,
                    "weaknessExposed": 62,
                    "authenticity": 64,
                    "surprise": 1,
                },
                "memorable_quote": "我们把问题摊开说。",
                "biggest_flaw": "时间表不够明确",
                "media_angle": "漏洞放大",
                "stat_impact": StatsDelta(CASH=-2, MORALE=-3, BOARD=1, FACE=-1),
            }
        )


def test_company_template_and_uuid_validation_paths() -> None:
    company = Company.from_template(
        {
            "names": ["星火"],
            "businesses": ["卖月亮咖啡"],
            "absurdity": [3],
            "mottos": ["先活下去再说"],
            "death_causes": [
                DeathCause(category="financial", description="现金流断裂"),
                DeathCause(category="trust", description="信任同时坍塌"),
            ],
            "founded_years": [2024],
        },
        rng_seed=2,
    )

    assert company.starting_promises == []

    with pytest.raises(ValueError):
        Company(
            id="00000000-0000-1000-8000-000000000000",
            name="星火",
            business="卖月亮咖啡",
            absurdity=3,
            founding_motto="先活下去再说",
            death_causes=[
                DeathCause(category="financial", description="现金流断裂"),
                DeathCause(category="trust", description="信任同时坍塌"),
            ],
            founded_year=2024,
        )

    with pytest.raises(ValueError):
        Company.from_template(
            {
                "names": [],
                "businesses": ["卖月亮咖啡"],
                "absurdity": [3],
                "mottos": ["先活下去再说"],
                "death_causes": [
                    DeathCause(category="financial", description="现金流断裂"),
                    DeathCause(category="trust", description="信任同时坍塌"),
                ],
                "founded_years": [2024],
            }
        )

    with pytest.raises(KeyError):
        Company.from_template(
            {
                "businesses": ["卖月亮咖啡"],
                "absurdity": [3],
                "mottos": ["先活下去再说"],
                "death_causes": [
                    DeathCause(category="financial", description="现金流断裂"),
                    DeathCause(category="trust", description="信任同时坍塌"),
                ],
                "founded_years": [2024],
            }
        )
