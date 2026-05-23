"""Employee template registry."""

from __future__ import annotations

from copy import deepcopy
from random import Random
from typing import Any

EMPLOYEE_TEMPLATES: list[dict[str, Any]] = [
    {
        "template_id": "E-T-01",
        "role": "CEO 助理",
        "personality_tag": "CAUTIOUS",
        "faction": "NEUTRAL",
        "competence_range": [58, 76],
        "loyalty_range": [55, 82],
        "stress_range": [20, 48],
        "name_pool": ["林知夏", "周予安", "顾清妍", "许安然"],
        "relationships_seed": [
            {"target_template_id": "E-T-04", "type": "mentor", "strength": 60},
            {"target_template_id": "E-T-12", "type": "rival", "strength": 35},
        ],
        "hidden_secrets_pool": ["知道前任 CEO 的备忘录", "偷偷备份了会议纪要"],
        "quitting_risk_template": "看风向很快，压力过高易跳船",
    },
    {
        "template_id": "E-T-02",
        "role": "CFO",
        "personality_tag": "VETERAN",
        "faction": "FINANCE",
        "competence_range": [70, 90],
        "loyalty_range": [45, 72],
        "stress_range": [30, 60],
        "name_pool": ["陈砚", "梁书恒", "宋景和", "赵闻舟"],
        "relationships_seed": [
            {"target_template_id": "E-T-01", "type": "close_friend", "strength": 55},
            {"target_template_id": "E-T-09", "type": "faction_enemy", "strength": 65},
        ],
        "hidden_secrets_pool": ["账上有一笔未解释的备用金", "知道两个版本的现金预测"],
        "quitting_risk_template": "被逼背锅时最先考虑离开",
    },
    {
        "template_id": "E-T-03",
        "role": "CTO",
        "personality_tag": "GO_GETTER",
        "faction": "TECH",
        "competence_range": [78, 95],
        "loyalty_range": [35, 68],
        "stress_range": [25, 58],
        "name_pool": ["沈知远", "韩序", "唐予墨", "程砚秋", "陆行舟"],
        "relationships_seed": [
            {"target_template_id": "E-T-07", "type": "mentor", "strength": 50},
            {"target_template_id": "E-T-10", "type": "rival", "strength": 70},
        ],
        "hidden_secrets_pool": ["想把老系统全推倒重写", "私下收藏了竞品招聘页"],
        "quitting_risk_template": "技术理想受挫时容易出走",
    },
    {
        "template_id": "E-T-04",
        "role": "产品负责人",
        "personality_tag": "RADICAL",
        "faction": "TECH",
        "competence_range": [62, 85],
        "loyalty_range": [30, 65],
        "stress_range": [35, 70],
        "name_pool": ["方予晴", "夏景然", "叶临风", "顾一帆"],
        "relationships_seed": [
            {"target_template_id": "E-T-03", "type": "faction_ally", "strength": 55},
            {"target_template_id": "E-T-08", "type": "rival", "strength": 50},
        ],
        "hidden_secrets_pool": ["总想重做信息架构", "私下给竞品记过分"],
        "quitting_risk_template": "方向被否时会冲动提桶",
    },
    {
        "template_id": "E-T-05",
        "role": "HR 总监",
        "personality_tag": "GOOD_PERSON",
        "faction": "OPS",
        "competence_range": [60, 80],
        "loyalty_range": [58, 88],
        "stress_range": [18, 45],
        "name_pool": ["唐婉", "吴知微", "郑语安", "叶晴岚"],
        "relationships_seed": [
            {"target_template_id": "E-T-01", "type": "close_friend", "strength": 65},
            {"target_template_id": "E-T-11", "type": "mentor", "strength": 50},
        ],
        "hidden_secrets_pool": ["知道谁最先看空公司", "留着一份离职访谈记录"],
        "quitting_risk_template": "看见组织失序会先撑住再说",
    },
    {
        "template_id": "E-T-06",
        "role": "销售总监",
        "personality_tag": "GO_GETTER",
        "faction": "SALES",
        "competence_range": [68, 90],
        "loyalty_range": [32, 66],
        "stress_range": [28, 60],
        "name_pool": ["罗予衡", "贺知远", "杜明轩", "秦以安"],
        "relationships_seed": [
            {"target_template_id": "E-T-02", "type": "rival", "strength": 60},
            {"target_template_id": "E-T-12", "type": "faction_ally", "strength": 55},
        ],
        "hidden_secrets_pool": ["客户名单有一份备份在家里", "知道上一轮价格战的底线"],
        "quitting_risk_template": "业绩下滑时最先找退路",
    },
    {
        "template_id": "E-T-07",
        "role": "核心工程师 A",
        "personality_tag": "VETERAN",
        "faction": "TECH",
        "competence_range": [74, 93],
        "loyalty_range": [42, 78],
        "stress_range": [22, 54],
        "name_pool": ["秦知舟", "宋言初", "莫予安", "许南星"],
        "relationships_seed": [
            {"target_template_id": "E-T-03", "type": "mentor", "strength": 70},
            {"target_template_id": "E-T-08", "type": "close_friend", "strength": 45},
        ],
        "hidden_secrets_pool": ["掌握老系统最脏的接口", "一直在修补没人承认的债"],
        "quitting_risk_template": "老项目失宠时容易心凉",
    },
    {
        "template_id": "E-T-08",
        "role": "核心工程师 B",
        "personality_tag": "SLACKER",
        "faction": "TECH",
        "competence_range": [52, 74],
        "loyalty_range": [28, 60],
        "stress_range": [20, 50],
        "name_pool": ["林亦舟", "周默", "沈知意", "谢归远"],
        "relationships_seed": [
            {"target_template_id": "E-T-07", "type": "close_friend", "strength": 55},
            {"target_template_id": "E-T-10", "type": "mentor", "strength": 40},
        ],
        "hidden_secrets_pool": ["会把线上问题先记到明天", "知道谁在偷偷外包代码"],
        "quitting_risk_template": "节奏太紧就想先消失两天",
    },
    {
        "template_id": "E-T-09",
        "role": "摸鱼员工",
        "personality_tag": "SLACKER",
        "faction": "NEUTRAL",
        "competence_range": [30, 58],
        "loyalty_range": [38, 70],
        "stress_range": [10, 36],
        "name_pool": ["许小满", "蒋一然", "顾眠", "邓知夏"],
        "relationships_seed": [
            {"target_template_id": "E-T-05", "type": "mentor", "strength": 35},
            {"target_template_id": "E-T-10", "type": "rival", "strength": 25},
        ],
        "hidden_secrets_pool": ["摸鱼时写过一份竞品分析", "知道谁在茶水间抱怨最多"],
        "quitting_risk_template": "被点名就容易想躲开",
    },
    {
        "template_id": "E-T-10",
        "role": "激进员工",
        "personality_tag": "TROUBLEMAKER",
        "faction": "TECH",
        "competence_range": [48, 72],
        "loyalty_range": [22, 56],
        "stress_range": [40, 78],
        "name_pool": ["叶峥", "傅野", "韩屿", "夏言"],
        "relationships_seed": [
            {"target_template_id": "E-T-04", "type": "rival", "strength": 60},
            {"target_template_id": "E-T-03", "type": "faction_enemy", "strength": 45},
        ],
        "hidden_secrets_pool": ["老在群里发刺耳但有用的意见", "留着离职时的公开信草稿"],
        "quitting_risk_template": "与管理层冲突后最不稳定",
    },
    {
        "template_id": "E-T-11",
        "role": "老臣员工",
        "personality_tag": "VETERAN",
        "faction": "OPS",
        "competence_range": [58, 84],
        "loyalty_range": [50, 84],
        "stress_range": [18, 42],
        "name_pool": ["周启明", "唐守正", "梁景行", "顾长安"],
        "relationships_seed": [
            {"target_template_id": "E-T-02", "type": "close_friend", "strength": 50},
            {"target_template_id": "E-T-05", "type": "mentor", "strength": 45},
        ],
        "hidden_secrets_pool": ["见过公司第一份章程", "知道很多旧账该怎么翻"],
        "quitting_risk_template": "被新管理层忽视时会冷掉",
    },
    {
        "template_id": "E-T-12",
        "role": "叛逃种子员工",
        "personality_tag": "DEFECTOR",
        "faction": "NEUTRAL",
        "competence_range": [55, 82],
        "loyalty_range": [10, 45],
        "stress_range": [42, 86],
        "name_pool": ["许归舟", "沈离", "宋未央", "韩知退"],
        "relationships_seed": [
            {"target_template_id": "E-T-06", "type": "rival", "strength": 50},
            {"target_template_id": "E-T-01", "type": "faction_enemy", "strength": 40},
        ],
        "hidden_secrets_pool": ["手里有对外联络人名单", "已经看过别家 offer", "知道谁最先会跳"],
        "quitting_risk_template": "只要外部机会够好就会走",
    },
]

__all__ = (
    "EMPLOYEE_TEMPLATES",
    "get_employee_template_by_id",
    "get_employee_templates",
    "sample_employee_set",
)


def get_employee_templates() -> list[dict[str, Any]]:
    return deepcopy(EMPLOYEE_TEMPLATES)


def get_employee_template_by_id(id: str) -> dict[str, Any] | None:
    for template in EMPLOYEE_TEMPLATES:
        if template["template_id"] == id:
            return deepcopy(template)
    return None


def sample_employee_set(rng_seed: int | None = None) -> list[dict[str, Any]]:
    rng = Random(rng_seed)
    templates = deepcopy(EMPLOYEE_TEMPLATES)
    rng.shuffle(templates)
    return templates
