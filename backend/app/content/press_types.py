"""Press type registry."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

PRESS_TYPES: dict[str, dict[str, Any]] = {
    "INAUGURATION": {
        "title_zh": "就职答记者问",
        "trigger_condition_text": "新 CEO 上任后的首次公开露面",
        "must_answer_topics": ["团队稳定", "未来三季目标", "个人责任"],
        "difficulty": 2,
        "press_keywords": ["就职", "愿景", "稳定"],
    },
    "CRISIS": {
        "title_zh": "危机回应会",
        "trigger_condition_text": "现金流、裁员或舆情失控时的回应场合",
        "must_answer_topics": ["坏消息来源", "止血计划", "外界质疑"],
        "difficulty": 5,
        "press_keywords": ["危机", "解释", "现金流"],
    },
    "PRODUCT": {
        "title_zh": "新品发布会",
        "trigger_condition_text": "新产品、功能或版本需要对外发布",
        "must_answer_topics": ["产品亮点", "定价策略", "用户价值"],
        "difficulty": 3,
        "press_keywords": ["新品", "发布", "功能"],
    },
    "FINANCIAL": {
        "title_zh": "财务说明会",
        "trigger_condition_text": "投资人和媒体要求解释财务走势时",
        "must_answer_topics": ["收入变化", "成本结构", "现金储备"],
        "difficulty": 4,
        "press_keywords": ["财务", "利润", "现金"],
    },
    "ROADSHOW": {
        "title_zh": "路演沟通会",
        "trigger_condition_text": "需要向投资人讲清下一阶段计划时",
        "must_answer_topics": ["融资用途", "增长假设", "退出路径"],
        "difficulty": 4,
        "press_keywords": ["路演", "融资", "增长"],
    },
    "LAYOFF_EXPLAIN": {
        "title_zh": "裁员说明会",
        "trigger_condition_text": "裁员后对外说明组织调整原因",
        "must_answer_topics": ["裁员比例", "补偿方案", "未来安排"],
        "difficulty": 4,
        "press_keywords": ["裁员", "调整", "补偿"],
    },
    "REGULATOR": {
        "title_zh": "监管沟通会",
        "trigger_condition_text": "涉及合规、审查或主管部门沟通时",
        "must_answer_topics": ["合规动作", "整改计划", "配合态度"],
        "difficulty": 5,
        "press_keywords": ["监管", "合规", "整改"],
    },
    "COUNTER": {
        "title_zh": "反击回应会",
        "trigger_condition_text": "遭遇竞品攻击、抹黑或误读时",
        "must_answer_topics": ["事实澄清", "对手指控", "后续动作"],
        "difficulty": 3,
        "press_keywords": ["反击", "澄清", "指控"],
    },
}

__all__ = (
    "PRESS_TYPES",
    "get_default_press_for_quarter",
    "get_press_type_by_id",
    "list_press_types",
)


class _PressTypeEntry(BaseModel):
    model_config = ConfigDict(strict=True)

    title_zh: str
    trigger_condition_text: str
    must_answer_topics: list[str] = Field(min_length=3, max_length=3)
    difficulty: int = Field(ge=1, le=5)
    press_keywords: list[str] = Field(min_length=1)


def get_press_type_by_id(press_id: str) -> dict[str, Any] | None:
    entry = PRESS_TYPES.get(press_id)
    return deepcopy(entry) if entry is not None else None


def list_press_types() -> list[dict[str, Any]]:
    return [deepcopy(entry) for entry in PRESS_TYPES.values()]


def get_default_press_for_quarter(q: int) -> str | None:
    if q == 3:
        return "CRISIS"
    return None
