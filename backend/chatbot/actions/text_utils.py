"""Text parsing helpers used by Rasa actions."""

from __future__ import annotations

import re
import unicodedata
from typing import Any, List, Optional, Tuple

import pandas as pd
from rasa_sdk import Tracker


def normalize_text(value: Any) -> str:
    """Lowercase and remove accents for robust Vietnamese matching."""
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return ""
    text = unicodedata.normalize("NFD", str(value).lower().strip())
    text = "".join(ch for ch in text if unicodedata.category(ch) != "Mn")
    text = text.replace("đ", "d")
    return re.sub(r"\s+", " ", unicodedata.normalize("NFKC", text))


def parse_price(text: str) -> Tuple[Optional[int], Optional[int]]:
    """Parse Vietnamese min/max price expressions into VND."""
    norm = normalize_text(text)
    pattern = r"(\d+(?:[,.]\d+)?)\s*(k|nghin|ngan|tr|trieu|m|vnd|dong|d)?"
    amounts: List[int] = []
    for match in re.finditer(pattern, norm):
        raw, unit = match.group(1), match.group(2)
        ctx = norm[max(0, match.start() - 12) : match.end() + 12]
        if unit is None and re.search(
            r"\b(gb|tb|ram|rom|inch|hz|mah|mp|core|gen|iphone|galaxy|redmi)\b", ctx
        ):
            continue
        if unit is None and not re.search(r"\b(gia|tam|khoang|duoi|tren|tu|den|ngan sach)\b", ctx):
            continue
        value = float(raw.replace(",", "."))
        if unit in {"k", "nghin", "ngan"}:
            value *= 1_000
        elif unit in {"tr", "trieu", "m"}:
            value *= 1_000_000
        elif unit is None and 1 <= value <= 300:
            value *= 1_000_000
        amounts.append(int(value))

    if not amounts:
        return None, None

    is_range = re.search(r"\btu\b.+\b(den|toi|-)\b", norm)
    is_min = re.search(r"\b(tu|tren|hon|it nhat|toi thieu)\b", norm)
    is_max = re.search(r"\b(duoi|khong qua|toi da|tam|khoang|khoan)\b", norm)
    if is_range and len(amounts) >= 2:
        return min(amounts[:2]), max(amounts[:2])
    if is_min and not is_max:
        return amounts[0], None
    return None, max(amounts)


def latest_entity(tracker: Tracker, entity_name: str) -> Optional[str]:
    """Return an entity from the latest message only."""
    for ent in reversed(tracker.latest_message.get("entities", [])):
        if ent.get("entity") == entity_name and ent.get("value"):
            return str(ent["value"])
    return None
