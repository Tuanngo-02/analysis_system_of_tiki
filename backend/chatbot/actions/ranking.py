"""Product retrieval and ranking logic."""

from __future__ import annotations

import math
import re
from typing import List, Optional

import numpy as np
import pandas as pd

from .catalog import brand_terms, category_candidates
from .constants import CATEGORY_BY_PRODUCT, TOP_K_FAISS, TOP_K_RESPONSE
from .text_utils import normalize_text


def build_query(product: str, category: str, price_max: Optional[int], brand: Optional[str], config: Optional[str]) -> str:
    parts = [category, product]
    if brand and brand != "any":
        parts.append(str(brand))
    if config and config != "any":
        parts.append(str(config))
    if price_max:
        parts.append(f"giá dưới {price_max}")
    return " ".join(parts)


def query_terms(product: str, brand: Optional[str], config: Optional[str]) -> List[str]:
    """Build important terms that should appear in product names."""
    raw_terms: List[str] = []
    if product == "dien thoai":
        raw_terms.extend(["dien thoai"])
    elif product == "may tinh bang":
        raw_terms.extend(["may tinh bang", "tablet", "ipad"])
    elif CATEGORY_BY_PRODUCT.get(product) in {
        "Laptop May Vi Tinh Linh Kien",
        "Thiet Bi Kts Phu Kien So",
        "Balo Va Vali",
    }:
        accessory_terms = {
            "tai nghe": ["tai nghe", "headphone", "headset"],
            "chuot": ["chuot", "mouse"],
            "ban phim": ["ban phim", "keyboard"],
            "man hinh": ["man hinh", "monitor"],
            "usb": ["usb"],
            "o cung": ["o cung", "ssd", "hdd"],
            "ram": ["ram", "ddr", "laptop", "pc"],
            "cap ket noi": ["cap", "day cap", "usb", "type c", "hdmi"],
            "sac laptop": ["sac", "adapter", "charger", "laptop"],
            "pin laptop": ["pin", "battery", "laptop"],
            "loa may tinh": ["loa", "speaker", "may tinh"],
            "gia do laptop": ["gia do", "de laptop", "ke laptop", "de tan nhiet"],
            "tui laptop": ["tui", "balo", "chong soc", "laptop"],
        }
        raw_terms.extend(accessory_terms.get(product, [product]))
    elif product == "sach":
        raw_terms.extend(["sach", "truyen"])

    if brand and brand != "any":
        brand_norm = normalize_text(brand)
        raw_terms.append(brand_norm)
        if brand_norm == "apple":
            raw_terms.extend(["iphone", "ipad", "macbook"])

    if config and config != "any":
        config_norm = normalize_text(config)
        raw_terms.append(config_norm)
        raw_terms.extend(
            term
            for term in re.findall(r"[a-z0-9]+(?:\s+[a-z0-9]+)?", config_norm)
            if len(term) >= 3 and term not in {"ram", "rom", "gia", "duoi", "tren"}
        )

    terms = []
    for term in raw_terms:
        term = normalize_text(term)
        if term and term not in terms:
            terms.append(term)
    return terms


def add_name_price_scores(
    candidates: pd.DataFrame,
    product: str,
    price_min: Optional[int],
    price_max: Optional[int],
    brand: Optional[str],
    config: Optional[str],
) -> pd.DataFrame:
    """Score primarily by product name and price; rating is a small tie-breaker."""
    terms = query_terms(product, brand, config)
    name_norm = candidates["name"].fillna("").map(normalize_text)
    search_norm = candidates["search_text"].fillna("").map(normalize_text)

    name_score = pd.Series(0.0, index=candidates.index)
    for term in terms:
        name_hit = name_norm.str.contains(term, regex=False)
        search_hit = search_norm.str.contains(term, regex=False)
        name_score += name_hit.astype(float)
        name_score += (~name_hit & search_hit).astype(float) * 0.35

    if terms:
        name_score = (name_score / max(1.0, float(len(terms)))).clip(0, 1)
    else:
        name_score = pd.Series(0.5, index=candidates.index)

    price = pd.to_numeric(candidates["price"], errors="coerce")
    price_score = pd.Series(1.0, index=candidates.index)
    if price_max is not None and price_max > 0:
        price_score = (1 - ((price_max - price).abs() / price_max)).clip(lower=0, upper=1).fillna(0)
    elif price_min is not None and price_min > 0:
        price_score = (1 - ((price - price_min).abs() / price_min)).clip(lower=0, upper=1).fillna(0)

    similarity = pd.to_numeric(candidates.get("similarity", 0), errors="coerce").fillna(0).clip(0, 1)
    rating = pd.to_numeric(candidates["rating_average"], errors="coerce").fillna(0).clip(0, 5) / 5
    reviews = pd.to_numeric(candidates["review_count"], errors="coerce").fillna(0)
    review_score = np.log1p(reviews) / max(1.0, math.log1p(reviews.max() or 1))
    quality_score = (rating * 0.7) + (review_score * 0.3)

    candidates["name_score"] = name_score
    candidates["price_score"] = price_score
    candidates["quality_score"] = quality_score
    candidates["final_score"] = (
        candidates["name_score"] * 0.68
        + candidates["price_score"] * 0.17
        + similarity * 0.10
        + candidates["quality_score"] * 0.05
    )
    return candidates


def rank_products(
    model,
    index,
    products: pd.DataFrame,
    product: str,
    price_min: Optional[int],
    price_max: Optional[int],
    brand: Optional[str],
    config: Optional[str],
) -> pd.DataFrame:
    """Retrieve with FAISS when possible, then hard-filter and re-rank."""
    category = CATEGORY_BY_PRODUCT[product]
    hits = []
    if model is not None and index is not None:
        query = build_query(product, category, price_max, brand, config)
        embedding = model.encode(
            [query],
            normalize_embeddings=True,
            convert_to_numpy=True,
            show_progress_bar=False,
        ).astype("float32")
        scores, indices = index.search(embedding, TOP_K_FAISS)
        for score, idx in zip(scores[0], indices[0]):
            if 0 <= idx < len(products):
                row = products.iloc[int(idx)].to_dict()
                row["similarity"] = float(score)
                hits.append(row)

    faiss_df = pd.DataFrame(hits)
    lexical_df = category_candidates(products, product, brand, config)
    lexical_df["similarity"] = 0.55
    candidates = pd.concat([faiss_df, lexical_df], ignore_index=True)
    if candidates.empty:
        return candidates

    candidates = candidates.drop_duplicates("product_id")
    candidates = candidates[
        candidates["category"].fillna("").map(normalize_text).eq(normalize_text(category))
    ]
    candidates = category_candidates(candidates, product, brand, config)
    candidates["price"] = pd.to_numeric(candidates["price"], errors="coerce")
    if price_min is not None:
        candidates = candidates[candidates["price"] >= price_min]
    if price_max is not None:
        candidates = candidates[candidates["price"] <= price_max]
    if candidates.empty:
        return candidates

    terms = brand_terms(brand)
    if terms:
        brand_series = candidates["brand"].fillna("").map(normalize_text)
        name_norm = candidates["name"].fillna("").map(normalize_text)
        candidates = candidates[
            brand_series.apply(lambda x: any(term in x for term in terms))
            | name_norm.apply(lambda x: any(term in x for term in terms))
        ]
        if candidates.empty:
            return candidates

    candidates = add_name_price_scores(
        candidates=candidates,
        product=product,
        price_min=price_min,
        price_max=price_max,
        brand=brand,
        config=config,
    )
    return candidates.sort_values("final_score", ascending=False).head(TOP_K_RESPONSE)
