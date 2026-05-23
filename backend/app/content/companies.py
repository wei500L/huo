"""Company archetype templates."""

from __future__ import annotations

from copy import deepcopy
from random import Random
from typing import Any

COMPANY_TEMPLATES: list[dict[str, Any]] = [
    {
        "template_id": "C-01",
        "name_pool": ["星火冷柜", "星火智柜", "星火保鲜"],
        "business": "AI 情绪冰箱",
        "absurdity": 4,
        "founding_motto": "把情绪冻住再上班",
        "founded_year": 2024,
        "death_causes": [
            {"category": "financial", "description": "补贴烧完后，柜子只剩噪音"},
            {"category": "trust", "description": "用户怀疑冰箱在偷听家庭争吵"},
            {"category": "absurd", "description": "董事会要求给冰箱做 KPI"},
        ],
        "starting_promises": ["三个月铺满十城", "再也不碰价格战"],
        "stats_modifiers": {"CASH": -3, "MORALE": 2, "BOARD": -1, "FACE": 4},
    },
    {
        "template_id": "C-02",
        "name_pool": ["云鲸午睡舱", "云鲸歇歇站", "云鲸躺平仓"],
        "business": "共享午睡舱",
        "absurdity": 3,
        "founding_motto": "让疲惫也有排队秩序",
        "founded_year": 2023,
        "death_causes": [
            {"category": "market", "description": "商场改造后失去所有投放点位"},
            {"category": "financial", "description": "租金比午睡费更快上涨"},
        ],
        "starting_promises": ["每个园区都能午休", "绝不卖会员套路"],
        "stats_modifiers": {"CASH": 1, "MORALE": 3, "BOARD": 0, "FACE": -1},
    },
    {
        "template_id": "C-03",
        "name_pool": ["脉冲纪要", "脉冲会议锤", "脉冲速记"],
        "business": "AI 会议纪要锤",
        "absurdity": 2,
        "founding_motto": "开会要快，甩锅要准",
        "founded_year": 2022,
        "death_causes": [
            {"category": "product", "description": "模型总结太像老板口头禅"},
            {"category": "trust", "description": "员工发现纪要比人还会夸张"},
        ],
        "starting_promises": ["会议后 5 分钟出稿"],
        "stats_modifiers": {"CASH": 0, "MORALE": -1, "BOARD": 3, "FACE": 2},
    },
    {
        "template_id": "C-04",
        "name_pool": ["天台续命站", "天台回血机", "天台喘息亭"],
        "business": "情绪回血自助机",
        "absurdity": 5,
        "founding_motto": "先补血，再谈理想",
        "founded_year": 2025,
        "death_causes": [
            {"category": "absurd", "description": "机器被当成加班象征而遭抵制"},
            {"category": "market", "description": "写字楼客户转去买咖啡和按摩椅"},
            {"category": "financial", "description": "耗材和电费把利润吞光"},
        ],
        "starting_promises": ["让每个工位附近都有回血点"],
        "stats_modifiers": {"CASH": -2, "MORALE": 4, "BOARD": -2, "FACE": 1},
    },
    {
        "template_id": "C-05",
        "name_pool": ["面子星球", "面子替身团", "面子急救包"],
        "business": "危机公关替身团",
        "absurdity": 4,
        "founding_motto": "先保脸，再保命",
        "founded_year": 2021,
        "death_causes": [
            {"category": "trust", "description": "客户发现文案模板和道歉稿一模一样"},
            {"category": "market", "description": "舆情升级太快，替身跟不上"},
        ],
        "starting_promises": ["每次危机都能压住热搜"],
        "stats_modifiers": {"CASH": 2, "MORALE": -2, "BOARD": 1, "FACE": 5},
    },
    {
        "template_id": "C-06",
        "name_pool": ["极昼加班水", "极昼续航液", "极昼提神饮"],
        "business": "功能饮料订阅制",
        "absurdity": 3,
        "founding_motto": "把清醒卖成月费",
        "founded_year": 2026,
        "death_causes": [
            {"category": "product", "description": "用户嫌味道像熬夜后的键盘"},
            {"category": "financial", "description": "复购太低，库存越滚越大"},
            {"category": "trust", "description": "成分表被放大镜审查"},
        ],
        "starting_promises": ["每周准时送达"],
        "stats_modifiers": {"CASH": 3, "MORALE": -1, "BOARD": 0, "FACE": -2},
    },
]

__all__ = (
    "COMPANY_TEMPLATES",
    "get_company_template_by_id",
    "get_company_templates",
    "sample_company_template",
)


def get_company_templates() -> list[dict[str, Any]]:
    return deepcopy(COMPANY_TEMPLATES)


def get_company_template_by_id(template_id: str) -> dict[str, Any] | None:
    for template in COMPANY_TEMPLATES:
        if template["template_id"] == template_id:
            return deepcopy(template)
    return None


def sample_company_template(rng_seed: int | None = None) -> dict[str, Any]:
    rng = Random(rng_seed)
    return deepcopy(rng.choice(COMPANY_TEMPLATES))
