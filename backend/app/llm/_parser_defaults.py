"""Canonical parser fallback shapes."""

from __future__ import annotations

from typing import Any

from .schema import SCORE_KEYS


def canonical_director_base() -> dict[str, Any]:
    return {
        "boardReaction": {"speech": "先看结果，再看解释。", "patienceDelta": -1, "vote": "abstain"},
        "employeeGossip": {"speaker": "小周", "line": "今晚怕是又要加班复盘。", "mood": "anxious"},
        "mediaHeadline": {"outlet": "虎嗅", "headline": "公司先止血再求活路", "tone": "negative"},
        "rivalAction": {
            "rival": "老对手",
            "action": "wait",
            "move": "先观察空档，准备趁乱抢客户。",
            "expectedDamage": {"CASH": -2, "MORALE": 0, "BOARD": 0, "FACE": -2},
        },
        "marketSignal": "bear",
        "metricsDelta": {"CASH": -1, "MORALE": -2, "BOARD": 0, "FACE": -3},
        "quarterReport": (
            "董事会暂时收住火气，但并没有真正放松警惕；员工在茶水间里反复咀嚼组织调整的信号，"
            "媒体盯住现金流和执行节奏，对手保持克制，市场则把这家公司视为一场还没结束的止血实验。"
        ),
    }


def canonical_press_base() -> dict[str, Any]:
    return {
        "scores": {key: 50 for key in SCORE_KEYS},
        "memorableQuote": "我们不回避问题，但也不会靠口号续命。",
        "biggestFlaw": "回答节奏偏稳，缺少一个可以被媒体直接抓住的动作。",
        "mediaAngle": "模糊带过",
        "metricsDelta": {"CASH": -1, "MORALE": 1, "BOARD": 0, "FACE": 2},
        "internalEval": "覆盖了关键问题，风险控制较稳，但明确承诺仍然不足。",
    }


def canonical_death_base() -> dict[str, Any]:
    return {
        "obituary": (
            "这一轮结束时，公司已经没有继续把故事讲圆的余地。现金流先于信心被消耗殆尽，"
            "组织调整来得太晚，对外解释始终慢半拍，对内则在犹豫、观望与自我安慰之间不断拉扯。"
            "最后的崩塌不是某一个瞬间造成的，而是多次拖延、误判和过度自信叠加后的结果。"
            "留下来的不是胜利者的余韵，而是一份带着代价的教训：真正致命的并不只是坏消息本身，"
            "而是明明看见坏消息来了，却还想用更大的沉默把它盖住。"
        ),
        "biggestMistakeDecisionId": "DEC-Q3-LAYOFF",
        "lastEmployee": None,
        "headlines": ["止血动作来得太晚", "组织信心持续下滑", "市场开始重新定价"],
        "legacyUnlocks": ["PR_EXPERIENCE", "EMPLOYEE_TRUST"],
    }
