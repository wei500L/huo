"""Brand blacklist helpers."""

from __future__ import annotations

import re
from functools import lru_cache
from pathlib import Path

__all__ = ("find_brand_hits", "load_brand_blacklist")

_DEFAULT_BLACKLIST_PATH = Path(__file__).resolve().parents[2] / "docs" / "brand_blacklist.txt"


@lru_cache(maxsize=None)  # noqa: UP033
def load_brand_blacklist(path: Path | None = None) -> set[str]:
    """Load brand names from the bundled blacklist file."""

    blacklist_path = path or _DEFAULT_BLACKLIST_PATH
    entries: set[str] = set()
    with blacklist_path.open("r", encoding="utf-8") as handle:
        for line in handle:
            item = line.strip()
            if not item or item.startswith("#"):
                continue
            entries.add(item)
    return entries


def find_brand_hits(
    text: str,
    blacklist: set[str] | None = None,
) -> list[tuple[int, int, str]]:
    """Return all blacklist matches in a transcript."""

    entries = blacklist if blacklist is not None else load_brand_blacklist()
    hits: list[tuple[int, int, str]] = []
    for brand in sorted(entries, key=lambda item: (-len(item), item.casefold())):
        flags = re.IGNORECASE if brand.isascii() else 0
        for match in re.finditer(re.escape(brand), text, flags):
            hits.append((match.start(), match.end(), brand))
    hits.sort(key=lambda item: (item[0], item[1], item[2].casefold()))
    return hits
