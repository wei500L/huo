"""Gossip clue template pool."""

from __future__ import annotations

from copy import deepcopy
from random import Random
from typing import Any

from app.domain import Employee, GossipReliability

GOSSIP_TEMPLATES: dict[str, list[dict[str, Any]]] = {
    "tearoom": [
        {
            "template_id": "G-tearoom-01",
            "scene": "tearoom",
            "text_template": "{speaker}({role}) 说茶水间又在传新的版本",
            "reliability_distribution": {"RUMOR": 0.3, "LIKELY": 0.5, "CONFIRMED": 0.2},
            "truth_probability": 0.35,
            "ap_cost": 1,
            "linked_role_tags": ["CFO", "HR"],
        },
        {
            "template_id": "G-tearoom-02",
            "scene": "tearoom",
            "text_template": "{speaker}({role}) 低声说有人已经开始找下家",
            "reliability_distribution": {"RUMOR": 0.25, "LIKELY": 0.5, "CONFIRMED": 0.25},
            "truth_probability": 0.42,
            "ap_cost": 1,
            "linked_role_tags": ["HR", "VETERAN"],
        },
        {
            "template_id": "G-tearoom-03",
            "scene": "tearoom",
            "text_template": "{speaker}({role}) 说新预算表和旧口径对不上",
            "reliability_distribution": {"RUMOR": 0.35, "LIKELY": 0.45, "CONFIRMED": 0.2},
            "truth_probability": 0.3,
            "ap_cost": 1,
            "linked_role_tags": ["CFO", "FINANCE"],
        },
        {
            "template_id": "G-tearoom-04",
            "scene": "tearoom",
            "text_template": "{speaker}({role}) 提到董事会那边也开始急了",
            "reliability_distribution": {"RUMOR": 0.3, "LIKELY": 0.45, "CONFIRMED": 0.25},
            "truth_probability": 0.5,
            "ap_cost": 1,
            "linked_role_tags": ["BOARD", "OPS"],
        },
    ],
    "elevator": [
        {
            "template_id": "G-elevator-01",
            "scene": "elevator",
            "text_template": "{speaker}({role}) 说上周那个承诺已经变味",
            "reliability_distribution": {"RUMOR": 0.28, "LIKELY": 0.52, "CONFIRMED": 0.2},
            "truth_probability": 0.4,
            "ap_cost": 1,
            "linked_role_tags": ["CEO", "CTO"],
        },
        {
            "template_id": "G-elevator-02",
            "scene": "elevator",
            "text_template": "{speaker}({role}) 在门快关时补了一句：人已经在动",
            "reliability_distribution": {"RUMOR": 0.32, "LIKELY": 0.48, "CONFIRMED": 0.2},
            "truth_probability": 0.33,
            "ap_cost": 1,
            "linked_role_tags": ["TECH", "OPS"],
        },
        {
            "template_id": "G-elevator-03",
            "scene": "elevator",
            "text_template": "{speaker}({role}) 说下季度预算会被重新排",
            "reliability_distribution": {"RUMOR": 0.25, "LIKELY": 0.5, "CONFIRMED": 0.25},
            "truth_probability": 0.47,
            "ap_cost": 1,
            "linked_role_tags": ["CFO", "BOARD"],
        },
        {
            "template_id": "G-elevator-04",
            "scene": "elevator",
            "text_template": "{speaker}({role}) 提醒大家别在群里乱说话",
            "reliability_distribution": {"RUMOR": 0.3, "LIKELY": 0.5, "CONFIRMED": 0.2},
            "truth_probability": 0.25,
            "ap_cost": 1,
            "linked_role_tags": ["HR", "NEUTRAL"],
        },
    ],
    "meeting_room": [
        {
            "template_id": "G-meeting_room-01",
            "scene": "meeting_room",
            "text_template": "{speaker}({role}) 说会上有人被当场改口",
            "reliability_distribution": {"RUMOR": 0.3, "LIKELY": 0.45, "CONFIRMED": 0.25},
            "truth_probability": 0.38,
            "ap_cost": 1,
            "linked_role_tags": ["PRODUCT", "TECH"],
        },
        {
            "template_id": "G-meeting_room-02",
            "scene": "meeting_room",
            "text_template": "{speaker}({role}) 说会议纪要被删了一段",
            "reliability_distribution": {"RUMOR": 0.35, "LIKELY": 0.45, "CONFIRMED": 0.2},
            "truth_probability": 0.32,
            "ap_cost": 1,
            "linked_role_tags": ["CEO", "HR"],
        },
        {
            "template_id": "G-meeting_room-03",
            "scene": "meeting_room",
            "text_template": "{speaker}({role}) 说方案里最大的漏洞没人接",
            "reliability_distribution": {"RUMOR": 0.25, "LIKELY": 0.5, "CONFIRMED": 0.25},
            "truth_probability": 0.46,
            "ap_cost": 1,
            "linked_role_tags": ["CTO", "TECH"],
        },
        {
            "template_id": "G-meeting_room-04",
            "scene": "meeting_room",
            "text_template": "{speaker}({role}) 说董事会那边只想先看结果",
            "reliability_distribution": {"RUMOR": 0.28, "LIKELY": 0.47, "CONFIRMED": 0.25},
            "truth_probability": 0.44,
            "ap_cost": 1,
            "linked_role_tags": ["BOARD", "FINANCE"],
        },
    ],
    "workstation": [
        {
            "template_id": "G-workstation-01",
            "scene": "workstation",
            "text_template": "{speaker}({role}) 说工位边上的人已经开始偷摸投简历",
            "reliability_distribution": {"RUMOR": 0.33, "LIKELY": 0.47, "CONFIRMED": 0.2},
            "truth_probability": 0.36,
            "ap_cost": 1,
            "linked_role_tags": ["HR", "VETERAN"],
        },
        {
            "template_id": "G-workstation-02",
            "scene": "workstation",
            "text_template": "{speaker}({role}) 说老系统又把上线拖住了",
            "reliability_distribution": {"RUMOR": 0.26, "LIKELY": 0.49, "CONFIRMED": 0.25},
            "truth_probability": 0.48,
            "ap_cost": 1,
            "linked_role_tags": ["CTO", "TECH"],
        },
        {
            "template_id": "G-workstation-03",
            "scene": "workstation",
            "text_template": "{speaker}({role}) 说那个 KPI 现在看起来很危险",
            "reliability_distribution": {"RUMOR": 0.3, "LIKELY": 0.48, "CONFIRMED": 0.22},
            "truth_probability": 0.41,
            "ap_cost": 1,
            "linked_role_tags": ["CFO", "SALES"],
        },
        {
            "template_id": "G-workstation-04",
            "scene": "workstation",
            "text_template": "{speaker}({role}) 说有人在暗中整理离职名单",
            "reliability_distribution": {"RUMOR": 0.34, "LIKELY": 0.46, "CONFIRMED": 0.2},
            "truth_probability": 0.29,
            "ap_cost": 1,
            "linked_role_tags": ["HR", "OPS"],
        },
    ],
    "rooftop": [
        {
            "template_id": "G-rooftop-01",
            "scene": "rooftop",
            "text_template": "{speaker}({role}) 说楼下那波热闹只是开始",
            "reliability_distribution": {"RUMOR": 0.3, "LIKELY": 0.45, "CONFIRMED": 0.25},
            "truth_probability": 0.43,
            "ap_cost": 1,
            "linked_role_tags": ["RADICAL", "TROUBLEMAKER"],
        },
        {
            "template_id": "G-rooftop-02",
            "scene": "rooftop",
            "text_template": "{speaker}({role}) 说下个月可能又要改组织",
            "reliability_distribution": {"RUMOR": 0.28, "LIKELY": 0.5, "CONFIRMED": 0.22},
            "truth_probability": 0.39,
            "ap_cost": 1,
            "linked_role_tags": ["HR", "BOARD"],
        },
        {
            "template_id": "G-rooftop-03",
            "scene": "rooftop",
            "text_template": "{speaker}({role}) 说现金紧得像只剩下最后一口气",
            "reliability_distribution": {"RUMOR": 0.25, "LIKELY": 0.5, "CONFIRMED": 0.25},
            "truth_probability": 0.51,
            "ap_cost": 1,
            "linked_role_tags": ["CFO", "FINANCE"],
        },
        {
            "template_id": "G-rooftop-04",
            "scene": "rooftop",
            "text_template": "{speaker}({role}) 说老板自己也在等更坏的消息",
            "reliability_distribution": {"RUMOR": 0.33, "LIKELY": 0.44, "CONFIRMED": 0.23},
            "truth_probability": 0.34,
            "ap_cost": 1,
            "linked_role_tags": ["CEO", "NEUTRAL"],
        },
    ],
    "smoking_area": [
        {
            "template_id": "G-smoking_area-01",
            "scene": "smoking_area",
            "text_template": "{speaker}({role}) 说那份通知不会只改一页",
            "reliability_distribution": {"RUMOR": 0.27, "LIKELY": 0.5, "CONFIRMED": 0.23},
            "truth_probability": 0.37,
            "ap_cost": 1,
            "linked_role_tags": ["HR", "OPS"],
        },
        {
            "template_id": "G-smoking_area-02",
            "scene": "smoking_area",
            "text_template": "{speaker}({role}) 说对手已经盯上我们的人",
            "reliability_distribution": {"RUMOR": 0.3, "LIKELY": 0.47, "CONFIRMED": 0.23},
            "truth_probability": 0.45,
            "ap_cost": 1,
            "linked_role_tags": ["SALES", "TECH"],
        },
        {
            "template_id": "G-smoking_area-03",
            "scene": "smoking_area",
            "text_template": "{speaker}({role}) 说新方案还没过第一关",
            "reliability_distribution": {"RUMOR": 0.32, "LIKELY": 0.45, "CONFIRMED": 0.23},
            "truth_probability": 0.31,
            "ap_cost": 1,
            "linked_role_tags": ["PRODUCT", "CTO"],
        },
        {
            "template_id": "G-smoking_area-04",
            "scene": "smoking_area",
            "text_template": "{speaker}({role}) 说很多人都在等下一次裁决",
            "reliability_distribution": {"RUMOR": 0.29, "LIKELY": 0.48, "CONFIRMED": 0.23},
            "truth_probability": 0.42,
            "ap_cost": 1,
            "linked_role_tags": ["VETERAN", "BOARD"],
        },
    ],
}

__all__ = (
    "GOSSIP_TEMPLATES",
    "get_gossip_templates_by_scene",
    "sample_gossip_lead",
)


def get_gossip_templates_by_scene(scene: str) -> list[dict[str, Any]]:
    return [deepcopy(template) for template in GOSSIP_TEMPLATES.get(scene, [])]


def sample_gossip_lead(
    scene: str,
    employees: list[Employee],
    rng_seed: int | None = None,
) -> dict[str, Any]:
    if not employees:
        raise ValueError("employees cannot be empty")
    templates = GOSSIP_TEMPLATES.get(scene, [])
    if not templates:
        raise ValueError(f"unknown gossip scene: {scene}")
    rng = Random(rng_seed)
    template = deepcopy(rng.choice(templates))
    reliability = _sample_reliability(template["reliability_distribution"], rng)
    is_truth = rng.random() < template["truth_probability"]
    speaker = _pick_speaker(template["linked_role_tags"], employees, rng)
    rendered_text = template["text_template"].format(speaker=speaker.name, role=speaker.role)
    return {
        "template_id": template["template_id"],
        "scene": template["scene"],
        "speaker_id": speaker.id,
        "speaker_name": speaker.name,
        "speaker_role": speaker.role,
        "text": rendered_text,
        "reliability": reliability.value,
        "is_truth": is_truth,
        "ap_cost": template["ap_cost"],
        "linked_role_tags": list(template["linked_role_tags"]),
    }


def _pick_speaker(linked_role_tags: list[str], employees: list[Employee], rng: Random) -> Employee:
    tags = {tag.upper() for tag in linked_role_tags}
    matches = [
        employee
        for employee in employees
        if any(tag in employee.role.upper() for tag in tags)
    ]
    return rng.choice(matches if matches else employees)


def _sample_reliability(distribution: dict[str, float], rng: Random) -> GossipReliability:
    labels = list(distribution)
    weights = list(distribution.values())
    return GossipReliability(rng.choices(labels, weights=weights, k=1)[0])
