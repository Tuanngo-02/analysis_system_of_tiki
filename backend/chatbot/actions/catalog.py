"""Category and product-specific parsing/filtering logic."""

from __future__ import annotations

import re
from typing import Any, List, Optional

import pandas as pd

from .constants import (
    BRAND_DISPLAY_NAMES,
    CATEGORY_BY_PRODUCT,
    DEVICE_BRANDS,
    DISPLAY_PRODUCT,
    NO_PREFERENCE,
)
from .text_utils import normalize_text


def infer_product(text: str) -> Optional[str]:
    """Infer supported product type from text."""
    norm = normalize_text(text)
    if any(x in norm for x in ["sach", "truyen", "tieu thuyet", "manga", "conan"]):
        return "sach"
    if any(x in norm for x in ["tai nghe", "headphone", "headset"]):
        return "tai nghe"
    if any(x in norm for x in ["chuot", "mouse"]):
        return "chuot"
    if any(x in norm for x in ["ban phim", "keyboard"]):
        return "ban phim"
    if any(x in norm for x in ["man hinh", "monitor"]):
        return "man hinh"
    if any(x in norm for x in ["o cung", "ssd", "hdd", "hard drive"]):
        return "o cung"
    if re.search(r"\bram\b", norm) and not any(x in norm for x in ["kinh ram", "rau ram"]):
        return "ram"
    if any(x in norm for x in ["usb", "flash drive"]):
        return "usb"
    if any(x in norm for x in ["cap ket noi", "day cap", "cap usb", "cap mang", "cap hdmi", "type c", "hdmi"]):
        return "cap ket noi"
    if any(x in norm for x in ["sac laptop", "adapter laptop", "sac may tinh"]):
        return "sac laptop"
    if any(x in norm for x in ["pin laptop", "pin may tinh"]):
        return "pin laptop"
    if any(x in norm for x in ["loa may tinh", "loa vi tinh", "speaker"]):
        return "loa may tinh"
    if any(x in norm for x in ["gia do laptop", "de laptop", "ke laptop", "de tan nhiet"]):
        return "gia do laptop"
    if any(x in norm for x in ["tui chong soc", "balo laptop", "tui laptop", "cap laptop"]):
        return "tui laptop"
    if any(x in norm for x in ["may tinh bang", "tablet", "ipad"]):
        return "may tinh bang"
    if any(x in norm for x in ["dien thoai", "smartphone", "iphone", "samsung", "xiaomi", "oppo"]):
        return "dien thoai"
    return None


def canonical_product(value: Any) -> Optional[str]:
    """Convert NLU entity/user text to the internal product key."""
    norm = normalize_text(value)
    if not norm:
        return None
    if norm in {"sach", "truyen", "tieu thuyet", "manga"}:
        return "sach"
    accessory_aliases = {
        "tai nghe": "tai nghe",
        "headphone": "tai nghe",
        "headset": "tai nghe",
        "chuot": "chuot",
        "mouse": "chuot",
        "ban phim": "ban phim",
        "keyboard": "ban phim",
        "man hinh": "man hinh",
        "monitor": "man hinh",
        "usb": "usb",
        "flash drive": "usb",
        "o cung": "o cung",
        "ssd": "o cung",
        "hdd": "o cung",
        "ram": "ram",
        "ram may tinh": "ram",
        "cap ket noi": "cap ket noi",
        "day cap": "cap ket noi",
        "cap usb": "cap ket noi",
        "cap mang": "cap ket noi",
        "cap hdmi": "cap ket noi",
        "type c": "cap ket noi",
        "hdmi": "cap ket noi",
        "sac laptop": "sac laptop",
        "adapter laptop": "sac laptop",
        "pin laptop": "pin laptop",
        "loa may tinh": "loa may tinh",
        "loa vi tinh": "loa may tinh",
        "speaker": "loa may tinh",
        "gia do laptop": "gia do laptop",
        "de laptop": "gia do laptop",
        "ke laptop": "gia do laptop",
        "de tan nhiet": "gia do laptop",
        "tui chong soc": "tui laptop",
        "balo laptop": "tui laptop",
        "tui laptop": "tui laptop",
        "cap laptop": "tui laptop",
    }
    if norm in accessory_aliases:
        return accessory_aliases[norm]
    if norm in {"dien thoai", "smartphone", "iphone"}:
        return "dien thoai"
    if norm in {"may tinh bang", "tablet", "ipad"}:
        return "may tinh bang"
    return infer_product(str(value))


def display_product(product: Any) -> str:
    """Return the Vietnamese label shown to users."""
    return DISPLAY_PRODUCT.get(str(product), str(product))


def infer_brand(text: str) -> Optional[str]:
    """Infer device brand. Books do not require this field."""
    norm = normalize_text(text)
    if norm in NO_PREFERENCE:
        return "any"
    for brand in DEVICE_BRANDS:
        if re.search(rf"\b{re.escape(brand)}\b", norm):
            return BRAND_DISPLAY_NAMES.get(brand, brand)
    return None


def brand_terms(brand: Optional[str]) -> List[str]:
    """Return normalized brand aliases used for hard filtering."""
    if not brand or brand == "any":
        return []
    brand_norm = normalize_text(brand)
    if brand_norm in NO_PREFERENCE:
        return []
    terms = [brand_norm]
    if brand_norm == "apple":
        terms.extend(["iphone", "ipad", "macbook"])
    return terms


def infer_config(text: str, product: Optional[str]) -> Optional[str]:
    """Infer model/config/need for phones or genre/title/author for books."""
    norm = normalize_text(text)
    if norm in NO_PREFERENCE:
        return "any"

    if product == "sach" or infer_product(text) == "sach":
        book_terms = [
            "tieu thuyet",
            "kinh doanh",
            "thieu nhi",
            "manga",
            "conan",
            "one piece",
            "ielts",
            "van hoc",
            "ky nang",
        ]
        found = [term for term in book_terms if term in norm]
        if found:
            return " ".join(found)
        cleaned = re.sub(r"\b(toi|minh|muon|mua|tim|sach|gia|duoi|tren|khoang|tam)\b", " ", norm)
        cleaned = re.sub(r"\d+(?:[,.]\d+)?\s*(k|nghin|ngan|tr|trieu|m|vnd|dong|d)?", " ", cleaned)
        cleaned = re.sub(r"\s+", " ", cleaned).strip()
        return cleaned or None

    patterns = [
        r"iphone\s*\d+\s*(pro max|pro|plus|mini)?",
        r"galaxy\s*[a-z]?\d+",
        r"redmi\s*\d+\w*",
        r"ram\s*\d+\s*gb",
        r"\d+\s*gb\s*ram",
        r"rom\s*\d+\s*gb",
        r"\d+\s*gb\s*rom",
        r"ssd\s*\d+\s*(gb|tb)",
        r"\d+\s*(gb|tb)\s*ssd",
        r"\bssd\b|\bhdd\b",
        r"\d+\s*gb",
        r"pin\s*(trau|tot|khoe)",
        r"camera\s*(dep|tot|xin)",
        r"choi game|gaming|game",
        r"choi game|gaming|game|van phong|hoc online|hoc tap",
        r"khong day|bluetooth|co day|chong on|rgb|co hoc",
        r"usb 3\.0|type[- ]?c|hdmi|cat6|gaming|van phong",
        r"ddr[345]|ddr\s*[345]",
        r"man hinh lon",
    ]
    found = [m.group(0) for p in patterns for m in re.finditer(p, norm)]
    if found:
        return " ".join(dict.fromkeys(found))
    return None


def category_candidates(
    products: pd.DataFrame,
    product: str,
    brand: Optional[str],
    config: Optional[str],
) -> pd.DataFrame:
    """Hard-filter products by supported category and important keywords."""
    category = CATEGORY_BY_PRODUCT[product]
    df = products[
        products["category"].fillna("").map(normalize_text).eq(normalize_text(category))
    ].copy()
    if df.empty:
        return df

    name_norm = df["name"].fillna("").map(normalize_text)

    if product == "dien thoai":
        df = df[
            (name_norm.str.contains("dien thoai", regex=False) | name_norm.str.contains("iphone", regex=False))
            & ~name_norm.str.contains("dien thoai ban", regex=False)
        ]
    elif product == "may tinh bang":
        df = df[
            name_norm.str.contains("may tinh bang", regex=False)
            | name_norm.str.contains("tablet", regex=False)
            | name_norm.str.contains("ipad", regex=False)
        ]
    elif product in CATEGORY_BY_PRODUCT and CATEGORY_BY_PRODUCT[product] in {
        "Laptop May Vi Tinh Linh Kien",
        "Thiet Bi Kts Phu Kien So",
        "Balo Va Vali",
    }:
        keywords_by_product = {
            "tai nghe": ["tai nghe", "headphone", "headset"],
            "chuot": ["chuot", "mouse"],
            "ban phim": ["ban phim", "keyboard"],
            "man hinh": ["man hinh", "monitor"],
            "usb": ["usb", "flash drive"],
            "o cung": ["o cung", "ssd", "hdd", "hard drive"],
            "ram": ["ram laptop", "ram pc", "ram ddr", "ram may tinh"],
            "cap ket noi": ["cap ket noi", "day cap", "cap usb", "cap mang", "cap hdmi", "type c", "hdmi"],
            "sac laptop": ["sac", "adapter", "charger"],
            "pin laptop": ["pin", "battery"],
            "loa may tinh": ["loa may tinh", "loa vi tinh", "speaker"],
            "gia do laptop": ["gia do laptop", "de laptop", "ke laptop", "de tan nhiet"],
            "tui laptop": ["tui chong soc", "balo laptop", "tui laptop", "cap laptop"],
        }
        keywords = keywords_by_product.get(product, [])
        mask = pd.Series(False, index=df.index)
        for keyword in keywords:
            mask = mask | name_norm.str.contains(keyword, regex=False)
        df = df[mask]
        if product == "ban phim" and not df.empty:
            exclude = pd.Series(False, index=df.index)
            for term in ["mieng ke", "dem lot", "lot chuot", "mouse pad"]:
                exclude = exclude | df["name"].fillna("").map(normalize_text).str.contains(term, regex=False)
            df = df[~exclude]
        if product == "ram" and not df.empty:
            exclude = pd.Series(False, index=df.index)
            for term in ["mainboard", "bo mach chu"]:
                exclude = exclude | df["name"].fillna("").map(normalize_text).str.contains(term, regex=False)
            df = df[~exclude]

    terms = brand_terms(brand)
    if terms:
        brand_series = df["brand"].fillna("").map(normalize_text)
        name_norm = df["name"].fillna("").map(normalize_text)
        df = df[
            brand_series.apply(lambda x: any(term in x for term in terms))
            | name_norm.apply(lambda x: any(term in x for term in terms))
        ]

    if config and config != "any":
        config_terms = [
            term
            for term in re.findall(r"[a-z0-9]+(?:\s+[a-z0-9]+)?", normalize_text(config))
            if len(term) >= 3 and term not in {"ram", "rom", "gia", "duoi", "tren"}
        ]
        if config_terms:
            name_norm = df["name"].fillna("").map(normalize_text)
            search_norm = df["search_text"].fillna("").map(normalize_text)
            mask = pd.Series(False, index=df.index)
            for term in config_terms:
                mask = mask | name_norm.str.contains(term, regex=False) | search_norm.str.contains(term, regex=False)
            if mask.any():
                df = df[mask]
            elif product == "ram":
                df = df[mask]
    return df
