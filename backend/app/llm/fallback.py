"""Deterministic fallback payloads for the LLM layer."""

from __future__ import annotations

import json
from typing import Literal

__all__ = (
    "STUB_DEATH_REPORT",
    "STUB_DIRECTOR",
    "STUB_PRESS_EVAL",
    "get_default_stub",
)

_DIRECTOR_STUB = {
    "boardReaction": {
        "speech": "先看结果，再看解释。",
        "patienceDelta": -1,
        "vote": "abstain",
    },
    "employeeGossip": {
        "speaker": "小周",
        "line": "今晚怕是又要加班复盘。",
        "mood": "anxious",
    },
    "mediaHeadline": {
        "outlet": "虎嗅",
        "headline": "公司先止血再求活路",
        "tone": "negative",
    },
    "rivalAction": {
        "rival": "老对手",
        "action": "wait",
        "move": "先观察空档，准备趁乱抢客户。",
        "expectedDamage": {"CASH": -2, "MORALE": 0, "BOARD": 0, "FACE": -2},
    },
    "marketSignal": "bear",
    "metricsDelta": {"CASH": -1, "MORALE": -2, "BOARD": 0, "FACE": -3},
    "quarterReport": (
        "董事会暂时收住火气，但并没有真正放松警惕；"
        "员工在茶水间里反复咀嚼组织调整的信号，"
        "媒体盯住现金流和执行节奏，"
        "对手保持克制，"
        "市场则把这家公司视为一场还没结束的止血实验。"
    ),
}

_PRESS_EVAL_STUB = {
    "scores": {
        "contentCompleteness": 72,
        "issueResponse": 66,
        "overpromise": 54,
        "logicClarity": 69,
        "confidence": 63,
        "riskAvoidance": 71,
        "memorableQuote": 79,
        "weaknessExposed": 58,
        "authenticity": 67,
    },
    "memorableQuote": "我们不回避问题，但也不会靠口号续命。",
    "biggestFlaw": "回答节奏偏稳，缺少一个可以被媒体直接抓住的动作。",
    "mediaAngle": "模糊带过",
    "metricsDelta": {"CASH": -1, "MORALE": 1, "BOARD": 0, "FACE": 2},
    "internalEval": (
        "覆盖了现金、组织和产品三条线，风险控制较稳，"
        "但对最尖锐的问题没有给出足够明确的承诺。"
    ),
}

_DEATH_REPORT_STUB = {
    "obituary": (
        "这一轮结束时，公司已经没有继续把故事讲圆的余地。"
        "现金流先于信心被消耗殆尽，组织调整来得太晚，"
        "对外解释始终慢半拍，"
        "对内则在犹豫、观望与自我安慰之间不断拉扯。"
        "最后的崩塌不是某一个瞬间造成的，而是多次拖延、误判和过度自信叠加后的结果。"
        "留下来的不是胜利者的余韵，而是一份带着代价的教训："
        "真正致命的并不只是坏消息本身，"
        "而是明明看见坏消息来了，却还想用更大的沉默把它盖住。"
        "如果还有下一次，管理层必须更早承认问题，"
        "更快给出取舍，"
        "也更诚实地告诉员工和市场：公司正在失去什么，"
        "又愿意为了活下来付出什么。"
    ),
    "biggestMistakeDecisionId": "DEC-Q3-LAYOFF",
    "lastEmployee": {"name": "小周", "line": "茶水间里只剩下沉默。"},
    "headlines": [
        "止血动作来得太晚",
        "组织信心持续下滑",
        "市场开始重新定价",
    ],
    "legacyUnlocks": ["PR_EXPERIENCE", "EMPLOYEE_TRUST"],
}

STUB_DIRECTOR = json.dumps(_DIRECTOR_STUB, ensure_ascii=False, separators=(",", ":"))
STUB_PRESS_EVAL = json.dumps(_PRESS_EVAL_STUB, ensure_ascii=False, separators=(",", ":"))
STUB_DEATH_REPORT = json.dumps(_DEATH_REPORT_STUB, ensure_ascii=False, separators=(",", ":"))

_STUBS: dict[str, str] = {
    "director": STUB_DIRECTOR,
    "press_eval": STUB_PRESS_EVAL,
    "death_report": STUB_DEATH_REPORT,
}


def get_default_stub(kind: Literal["director", "press_eval", "death_report"]) -> str:
    """Return the deterministic fallback payload for a prompt kind."""

    return _STUBS[kind]
