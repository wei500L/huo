"""Tests for the in-memory press archive repository."""

from __future__ import annotations

import re

import pytest

from app.domain import MediaHeadline, PressBundle
from app.repo.memory_impl import InMemoryPressArchiveRepo
from tests.factories import build_press_evaluation, build_press_input


def _build_bundle(tag: str) -> PressBundle:
    return PressBundle(
        input=build_press_input(
            transcript=(
                f"我们正在处理 {tag} 的问题，并持续回应市场关切，"
                "同时向董事会、员工和媒体说明当前进展。"
            )
        ),
        evaluation=build_press_evaluation(),
        headlines=[
            MediaHeadline(
                outlet="36 氪",
                headline=f"{tag} 标题",
                tone="neutral",
            ),
        ],
    )


@pytest.mark.asyncio
async def test_append_returns_archive_id_shape() -> None:
    repo = InMemoryPressArchiveRepo()

    archive_id = await repo.append("S-0001", _build_bundle("A"))

    assert re.fullmatch(r"P-[0-9a-f]{10}", archive_id)


@pytest.mark.asyncio
async def test_list_by_session_preserves_append_order() -> None:
    repo = InMemoryPressArchiveRepo()
    first = _build_bundle("A")
    second = _build_bundle("B")

    first_id = await repo.append("S-0001", first)
    second_id = await repo.append("S-0001", second)

    bundles = await repo.list_by_session("S-0001")

    assert bundles == [first, second]
    assert await repo.get(first_id) == first
    assert await repo.get(second_id) == second
