"""Legacy and management-style unlock resolution."""

from __future__ import annotations

from collections.abc import Callable, Iterable
from dataclasses import dataclass

from pydantic import BaseModel, ConfigDict, Field

from app.content.decisions import get_decision_card_by_id
from app.domain import (
    DeathReason,
    DecisionCategory,
    Employee,
    HistoryEntry,
    LegacyType,
    LegacyUnlock,
    ManagementStyle,
    MetaProgress,
    PressBundle,
    Promise,
)

__all__ = ("LegacyEvaluation", "LegacyResolver")


class LegacyEvaluation(BaseModel):
    """Unlocks earned by the just-finished run."""

    model_config = ConfigDict(frozen=True, strict=True)

    new_legacies: list[LegacyUnlock] = Field(default_factory=list)
    new_styles: list[ManagementStyle] = Field(default_factory=list)
    rationale: dict[str, str] = Field(default_factory=dict)


@dataclass(frozen=True)
class _LegacySpec:
    label_zh: str
    description: str
    effect_summary: str
    rationale: str


_LEGACY_SPECS: dict[LegacyType, _LegacySpec] = {
    LegacyType.PR_EXPERIENCE: _LegacySpec(
        "公关手感",
        "至少一次发布会信息完整度达标",
        "FACE +5",
        "发布会内容完整度达到 70。",
    ),
    LegacyType.FUNDING_PITCH: _LegacySpec(
        "融资话术",
        "融资决策后现金线仍稳住",
        "BOARD +3",
        "融资后现金没有跌破 20。",
    ),
    LegacyType.ORG_KNOWHOW: _LegacySpec(
        "组织肌肉",
        "整局士气没有跌破危险线",
        "MORALE +5",
        "所有季度士气均不低于 30。",
    ),
    LegacyType.PRODUCT_TASTE: _LegacySpec(
        "产品嗅觉",
        "做过关键产品取舍",
        "BOARD +4",
        "本局执行过转型或砍线。",
    ),
    LegacyType.MEDIA_NERVE: _LegacySpec(
        "媒体胆量", "至少一次发布会表现出足够气势", "FACE +5", "发布会 confidence 达到 60。"
    ),
    LegacyType.EMPLOYEE_TRUST: _LegacySpec(
        "员工信任", "撑过 Q4 且保住核心信任", "MORALE +4", "终局仍有至少 3 名高忠诚员工。"
    ),
    LegacyType.INDUSTRY_INTEL: _LegacySpec(
        "行业雷达", "经历过熊市或危机信号", "BOARD +4", "本局命中过 bear/crisis 市场信号。"
    ),
}

_STYLE_RATIONALE: dict[ManagementStyle, str] = {
    ManagementStyle.IRON_LAYOFF: "本局累计裁员决策达到 3 次。",
    ManagementStyle.STORY_MASTER: "发布会 authenticity 达到 70 至少 2 次。",
    ManagementStyle.DATA_FREAK: "已判定承诺履约率达到 80%。",
    ManagementStyle.FACE_KEEPER: "终局 FACE 不低于 60。",
    ManagementStyle.SURVIVAL_PRO: "最近 3 局都撑到 Q3 之后或通关。",
}


class LegacyResolver:
    """Evaluate DESIGN 13.4/13.5 unlock rules from settled run data."""

    def __init__(self) -> None:
        self._legacy_rules: dict[LegacyType, Callable[[_EvalInput], bool]] = {
            LegacyType.PR_EXPERIENCE: _has_content_complete_press,
            LegacyType.FUNDING_PITCH: _has_safe_funding,
            LegacyType.ORG_KNOWHOW: _kept_org_morale,
            LegacyType.PRODUCT_TASTE: _made_product_call,
            LegacyType.MEDIA_NERVE: _has_confident_press,
            LegacyType.EMPLOYEE_TRUST: _kept_employee_trust,
            LegacyType.INDUSTRY_INTEL: _saw_bad_market_signal,
        }
        self._style_rules: dict[ManagementStyle, Callable[[_EvalInput], bool]] = {
            ManagementStyle.IRON_LAYOFF: _made_three_layoffs,
            ManagementStyle.STORY_MASTER: _has_story_mastery,
            ManagementStyle.DATA_FREAK: _kept_promises,
            ManagementStyle.FACE_KEEPER: _kept_face,
            ManagementStyle.SURVIVAL_PRO: _is_survival_pro,
        }

    def evaluate(
        self,
        ctx_history: list[HistoryEntry],
        press_archive: list[PressBundle],
        meta_before: MetaProgress,
        died_at_quarter: int,
        death_reason: DeathReason | None,
        *,
        run_id: str = "unknown",
        employees_snapshot: list[Employee] | None = None,
        promise_log: list[Promise] | None = None,
    ) -> LegacyEvaluation:
        data = _EvalInput(
            history=ctx_history,
            press_archive=press_archive,
            meta_before=meta_before,
            died_at_quarter=died_at_quarter,
            death_reason=death_reason,
            run_id=run_id,
            employees_snapshot=employees_snapshot or [],
            promise_log=promise_log or [],
        )
        existing_legacies = {unlock.type for unlock in meta_before.unlocked_legacies}
        existing_styles = set(meta_before.unlocked_styles)
        new_legacies: list[LegacyUnlock] = []
        new_styles: list[ManagementStyle] = []
        rationale: dict[str, str] = {}

        for legacy_type, rule in self._legacy_rules.items():
            if legacy_type in existing_legacies or not rule(data):
                continue
            spec = _LEGACY_SPECS[legacy_type]
            new_legacies.append(
                LegacyUnlock(
                    type=legacy_type,
                    label_zh=spec.label_zh,
                    description=spec.description,
                    effect_summary=spec.effect_summary,
                    earned_at_run_id=run_id,
                    earned_at_quarter=died_at_quarter,
                )
            )
            rationale[legacy_type.value] = spec.rationale

        for style, rule in self._style_rules.items():
            if style in existing_styles or not rule(data):
                continue
            new_styles.append(style)
            rationale[style.value] = _STYLE_RATIONALE[style]

        return LegacyEvaluation(
            new_legacies=new_legacies,
            new_styles=new_styles,
            rationale=rationale,
        )


@dataclass(frozen=True)
class _EvalInput:
    history: list[HistoryEntry]
    press_archive: list[PressBundle]
    meta_before: MetaProgress
    died_at_quarter: int
    death_reason: DeathReason | None
    run_id: str
    employees_snapshot: list[Employee]
    promise_log: list[Promise]


def _scores(bundle: PressBundle) -> dict[str, int]:
    return {str(key): value for key, value in bundle.evaluation.scores.items()}


def _has_content_complete_press(data: _EvalInput) -> bool:
    return any(_scores(bundle).get("contentCompleteness", 0) >= 70 for bundle in data.press_archive)


def _has_safe_funding(data: _EvalInput) -> bool:
    return _count_decisions(data.history, {DecisionCategory.FUNDING}) >= 1 and all(
        entry.stats_after.CASH >= 20 for entry in data.history
    )


def _kept_org_morale(data: _EvalInput) -> bool:
    return bool(data.history) and all(entry.stats_after.MORALE >= 30 for entry in data.history)


def _made_product_call(data: _EvalInput) -> bool:
    return _count_decisions(
        data.history,
        {DecisionCategory.KILL_PRODUCT, DecisionCategory.PIVOT},
    ) >= 1


def _has_confident_press(data: _EvalInput) -> bool:
    return any(_scores(bundle).get("confidence", 0) >= 60 for bundle in data.press_archive)


def _kept_employee_trust(data: _EvalInput) -> bool:
    if data.died_at_quarter < 4 or data.death_reason is not None:
        return False
    return sum(1 for employee in data.employees_snapshot if employee.loyalty >= 70) >= 3


def _saw_bad_market_signal(data: _EvalInput) -> bool:
    return any(_entry_has_market_signal(entry, {"bear", "crisis"}) for entry in data.history)


def _made_three_layoffs(data: _EvalInput) -> bool:
    return _count_decisions(data.history, {DecisionCategory.LAYOFF}) >= 3


def _has_story_mastery(data: _EvalInput) -> bool:
    return (
        sum(1 for bundle in data.press_archive if _scores(bundle).get("authenticity", 0) >= 70)
        >= 2
    )


def _kept_promises(data: _EvalInput) -> bool:
    judged = [promise for promise in data.promise_log if promise.fulfilled is not None]
    if not judged:
        return False
    kept = sum(1 for promise in judged if promise.fulfilled is True)
    return kept / len(judged) >= 0.8


def _kept_face(data: _EvalInput) -> bool:
    return bool(data.history) and data.history[-1].stats_after.FACE >= 60


def _is_survival_pro(data: _EvalInput) -> bool:
    current_qualified = data.death_reason is None or data.died_at_quarter >= 3
    if not current_qualified:
        return False
    previous = list(data.meta_before.death_log)[-2:]
    if len(previous) < 2:
        return False
    return all(entry.death_reason is None or entry.died_at_quarter >= 3 for entry in previous)


def _count_decisions(history: Iterable[HistoryEntry], categories: set[DecisionCategory]) -> int:
    return sum(1 for entry in history if _decision_category(entry.decision_id) in categories)


def _decision_category(decision_id: str) -> DecisionCategory | None:
    card = get_decision_card_by_id(decision_id)
    if card is not None:
        return DecisionCategory(str(card["category"]))
    normalized = decision_id.upper().replace("-", "_")
    for category in DecisionCategory:
        if normalized == category.value or category.value in normalized:
            return category
    return None


def _entry_has_market_signal(entry: HistoryEntry, signals: set[str]) -> bool:
    direct_signal = getattr(entry, "market_signal", None)
    if isinstance(direct_signal, str) and direct_signal.lower() in signals:
        return True
    summary = entry.settlement_summary.lower()
    return any(signal in summary for signal in signals)
