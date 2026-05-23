"""Decision card templates."""

from __future__ import annotations

import logging
import re
from copy import deepcopy
from random import Random
from typing import Any

from app.domain import DecisionCategory, Stats

LOGGER = logging.getLogger(__name__)

DECISION_CARDS: list[dict[str, Any]] = [
    {
        "id": "D_FUNDING_01",
        "category": DecisionCategory.FUNDING.value,
        "title": "追投续命",
        "description": "再找一轮钱，先把窟窿堵住",
        "flavor": "投资人喜欢听故事，董事会喜欢看续表",
        "immediate_effect": {"CASH": 15, "MORALE": -2, "BOARD": 4, "FACE": -3},
        "long_term_hint": "条件会越来越硬",
        "boomerang_seeds": [
            {
                "delay_quarters": 2,
                "probability": 0.6,
                "description": "融资条款开始收紧",
                "effect": {"CASH": -4, "BOARD": -3},
            },
        ],
        "applicable_quarters": [1, 2, 3, 4],
        "applicable_when": ["CASH<40"],
    },
    {
        "id": "D_LAYOFF_01",
        "category": DecisionCategory.LAYOFF.value,
        "title": "裁员止血",
        "description": "先砍人头，现金流能多喘一口气",
        "flavor": "账面好看，气氛难看",
        "immediate_effect": {"CASH": 10, "MORALE": -12, "BOARD": 2, "FACE": -6},
        "long_term_hint": "核心员工会开始摇摆",
        "boomerang_seeds": [
            {
                "delay_quarters": 1,
                "probability": 0.7,
                "description": "骨干开始找下家",
                "effect": {"MORALE": -5, "FACE": -2},
            },
            {
                "delay_quarters": 2,
                "probability": 0.4,
                "description": "外部口碑继续下滑",
                "effect": {"FACE": -4},
            },
        ],
        "applicable_quarters": [1, 2, 3, 4],
        "applicable_when": ["MORALE<85"],
    },
    {
        "id": "D_SELL_ASSET_01",
        "category": DecisionCategory.SELL_ASSET.value,
        "title": "卖掉闲产",
        "description": "把还能卖的东西先卖掉",
        "flavor": "现金到账，骨气到账不了",
        "immediate_effect": {"CASH": 12, "MORALE": -3, "BOARD": -1, "FACE": -2},
        "long_term_hint": "可卖的东西会越来越少",
        "boomerang_seeds": [],
        "applicable_quarters": [1, 2, 3, 4],
        "applicable_when": ["CASH<50"],
    },
    {
        "id": "D_PIVOT_01",
        "category": DecisionCategory.PIVOT.value,
        "title": "方向重做",
        "description": "把旧产品线掀了，换一条路试试",
        "flavor": "会议室里所有人都很忙，只有方向在漂移",
        "immediate_effect": {"CASH": -3, "MORALE": -4, "BOARD": 3, "FACE": 1},
        "long_term_hint": "可能活，也可能更乱",
        "boomerang_seeds": [
            {
                "delay_quarters": 2,
                "probability": 0.5,
                "description": "新方向迟迟不落地",
                "effect": {"MORALE": -3, "BOARD": -2},
            },
        ],
        "applicable_quarters": [1, 2, 3, 4],
        "applicable_when": ["BOARD>30"],
    },
    {
        "id": "D_KILL_PRODUCT_01",
        "category": DecisionCategory.KILL_PRODUCT.value,
        "title": "砍掉旧线",
        "description": "停止继续烧钱的产品线",
        "flavor": "止损很理性，工位很沉默",
        "immediate_effect": {"CASH": 4, "MORALE": 3, "BOARD": 2, "FACE": -2},
        "long_term_hint": "砍得太慢就没意义",
        "boomerang_seeds": [],
        "applicable_quarters": [1, 2, 3, 4],
        "applicable_when": ["CASH>30"],
    },
    {
        "id": "D_PRICE_WAR_01",
        "category": DecisionCategory.PRICE_WAR.value,
        "title": "全面降价",
        "description": "拿价格把对手逼进角落",
        "flavor": "销量可能上来，利润先下去",
        "immediate_effect": {"CASH": -8, "MORALE": -2, "BOARD": -1, "FACE": -5},
        "long_term_hint": "最先疼的是自己",
        "boomerang_seeds": [
            {
                "delay_quarters": 1,
                "probability": 0.5,
                "description": "对手跟降更狠",
                "effect": {"CASH": -5, "FACE": -2},
            },
        ],
        "applicable_quarters": [1, 2, 3, 4],
        "applicable_when": ["FACE>20"],
    },
    {
        "id": "D_SOOTHE_01",
        "category": DecisionCategory.SOOTHE.value,
        "title": "安抚团队",
        "description": "给员工一点情绪修复时间",
        "flavor": "话术不值钱，真心值",
        "immediate_effect": {"CASH": -2, "MORALE": 8, "BOARD": 1, "FACE": 1},
        "long_term_hint": "要配合真动作",
        "boomerang_seeds": [],
        "applicable_quarters": [1, 2, 3, 4],
        "applicable_when": ["MORALE<95"],
    },
    {
        "id": "D_SWAP_EXEC_01",
        "category": DecisionCategory.SWAP_EXEC.value,
        "title": "换掉高管",
        "description": "把背锅位的人换下来",
        "flavor": "有人上桌，有人下桌",
        "immediate_effect": {"CASH": -1, "MORALE": -6, "BOARD": 5, "FACE": 2},
        "long_term_hint": "更换不会自动带来结果",
        "boomerang_seeds": [
            {
                "delay_quarters": 2,
                "probability": 0.5,
                "description": "交接期继续失控",
                "effect": {"BOARD": -2, "FACE": -1},
            },
        ],
        "applicable_quarters": [1, 2, 3, 4],
        "applicable_when": ["BOARD<80"],
    },
    {
        "id": "D_HIDE_BAD_NEWS_01",
        "category": DecisionCategory.HIDE_BAD_NEWS.value,
        "title": "压住坏消息",
        "description": "先别让外界知道真实情况",
        "flavor": "信息慢一点，麻烦不会慢",
        "immediate_effect": {"CASH": 0, "MORALE": -5, "BOARD": -4, "FACE": 3},
        "long_term_hint": "瞒得住一时瞒不住一季",
        "boomerang_seeds": [
            {
                "delay_quarters": 1,
                "probability": 0.8,
                "description": "消息反噬变成更大丑闻",
                "effect": {"FACE": -6, "BOARD": -3},
            },
        ],
        "applicable_quarters": [1, 2, 3, 4],
        "applicable_when": ["MORALE>20"],
    },
    {
        "id": "D_DELAY_BOARD_01",
        "category": DecisionCategory.DELAY_BOARD.value,
        "title": "拖住董事会",
        "description": "争取一季缓冲期",
        "flavor": "耐心是借来的",
        "immediate_effect": {"CASH": -2, "MORALE": 0, "BOARD": 4, "FACE": -2},
        "long_term_hint": "只适合有下一步时用",
        "boomerang_seeds": [],
        "applicable_quarters": [1, 2, 3, 4],
        "applicable_when": ["BOARD>20"],
    },
    {
        "id": "D_NEGOTIATE_RIVAL_01",
        "category": DecisionCategory.NEGOTIATE_RIVAL.value,
        "title": "和对手谈",
        "description": "试着把竞争变成合作",
        "flavor": "桌上谈判，桌下拔刀",
        "immediate_effect": {"CASH": 6, "MORALE": 1, "BOARD": 1, "FACE": 2},
        "long_term_hint": "合作条款会很脏",
        "boomerang_seeds": [
            {
                "delay_quarters": 3,
                "probability": 0.4,
                "description": "对手拿着协议反咬一口",
                "effect": {"FACE": -4},
            },
        ],
        "applicable_quarters": [1, 2, 3, 4],
        "applicable_when": ["CASH>20"],
    },
    {
        "id": "D_HUMILIATING_TERM_01",
        "category": DecisionCategory.HUMILIATING_TERM.value,
        "title": "签辱条约",
        "description": "换一口气，顺带吞下屈辱",
        "flavor": "现金到账，尊严离场",
        "immediate_effect": {"CASH": 18, "MORALE": -4, "BOARD": -5, "FACE": -8},
        "long_term_hint": "后面要付更大代价",
        "boomerang_seeds": [
            {
                "delay_quarters": 1,
                "probability": 0.7,
                "description": "外部条件变得更苛刻",
                "effect": {"BOARD": -3, "FACE": -3},
            },
            {
                "delay_quarters": 2,
                "probability": 0.5,
                "description": "内部士气继续受挫",
                "effect": {"MORALE": -4},
            },
        ],
        "applicable_quarters": [1, 2, 3, 4],
        "applicable_when": ["CASH<20"],
    },
]

__all__ = (
    "DECISION_CARDS",
    "get_all_decision_cards",
    "get_decision_card_by_id",
    "sample_decision_cards",
)

_APPLICABLE_RE = re.compile(r"^(CASH|MORALE|BOARD|FACE)\s*(<=|>=|<|>|==|=)\s*(-?\d+)$")


def get_all_decision_cards() -> list[dict[str, Any]]:
    return deepcopy(DECISION_CARDS)


def get_decision_card_by_id(card_id: str) -> dict[str, Any] | None:
    for card in DECISION_CARDS:
        if card["id"] == card_id:
            return deepcopy(card)
    return None


def sample_decision_cards(
    n: int = 3,
    quarter: int = 1,
    current_stats: Stats | None = None,
    rng_seed: int | None = None,
) -> list[dict[str, Any]]:
    rng = Random(rng_seed)
    eligible = [
        card
        for card in DECISION_CARDS
        if quarter in card["applicable_quarters"]
        and (
            current_stats is None
            or all(
                _condition_passes(condition, current_stats)
                for condition in card["applicable_when"]
            )
        )
    ]
    if not eligible:
        raise ValueError("no decision cards match the requested filters")
    if len(eligible) >= n:
        return [deepcopy(card) for card in rng.sample(eligible, n)]
    LOGGER.warning("decision card pool smaller than requested sample; duplicating draws")
    sampled = [deepcopy(card) for card in rng.sample(eligible, len(eligible))]
    while len(sampled) < n:
        sampled.append(deepcopy(rng.choice(eligible)))
    return sampled


def _condition_passes(condition: str, stats: Stats) -> bool:
    match = _APPLICABLE_RE.fullmatch(condition.strip())
    if match is None:
        raise ValueError(f"unsupported applicable_when condition: {condition}")
    field, operator, threshold_text = match.groups()
    stat_value = {
        "CASH": stats.CASH,
        "MORALE": stats.MORALE,
        "BOARD": stats.BOARD,
        "FACE": stats.FACE,
    }[field]
    threshold = int(threshold_text)
    if operator in ("<", "<="):
        return stat_value < threshold if operator == "<" else stat_value <= threshold
    if operator in (">", ">="):
        return stat_value > threshold if operator == ">" else stat_value >= threshold
    return stat_value == threshold
