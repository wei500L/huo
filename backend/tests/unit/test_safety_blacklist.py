"""Tests for brand blacklist helpers."""

from __future__ import annotations

from pathlib import Path

from app.safety.brand_blacklist import find_brand_hits, load_brand_blacklist


def test_load_brand_blacklist_uses_cache_once(monkeypatch) -> None:
    load_brand_blacklist.cache_clear()
    calls = {"count": 0}
    original_open = Path.open

    def counting_open(self: Path, *args, **kwargs):  # type: ignore[no-untyped-def]
        calls["count"] += 1
        return original_open(self, *args, **kwargs)

    monkeypatch.setattr(Path, "open", counting_open)

    first = load_brand_blacklist()
    second = load_brand_blacklist()

    assert first == second
    assert calls["count"] == 1
    assert len(first) >= 30


def test_find_brand_hits_returns_positions_and_hits() -> None:
    blacklist = {"Google", "OpenAI", "百度", "腾讯"}
    text = "Google meets google with OpenAI plus 百度 and 腾讯."

    hits = find_brand_hits(text, blacklist)

    assert hits == [
        (text.index("Google"), text.index("Google") + len("Google"), "Google"),
        (text.index("google"), text.index("google") + len("google"), "Google"),
        (text.index("OpenAI"), text.index("OpenAI") + len("OpenAI"), "OpenAI"),
        (text.index("百度"), text.index("百度") + len("百度"), "百度"),
        (text.index("腾讯"), text.index("腾讯") + len("腾讯"), "腾讯"),
    ]


def test_find_brand_hits_handles_case_insensitive_english_and_exact_chinese() -> None:
    blacklist = {"Google", "腾讯"}

    english_hits = find_brand_hits("google and Google", blacklist)
    chinese_hits = find_brand_hits("腾讯 and 腾讯", blacklist)

    assert [hit[2] for hit in english_hits] == ["Google", "Google"]
    assert [hit[2] for hit in chinese_hits] == ["腾讯", "腾讯"]
