"""Response formatting and slot serialization helpers."""

from __future__ import annotations

from typing import Any, List, Optional

import pandas as pd


def format_price(value: Any) -> str:
    price = pd.to_numeric(value, errors="coerce")
    if pd.isna(price):
        return "chưa rõ giá"
    return f"{int(price):,}đ".replace(",", ".")


def format_products(products: pd.DataFrame, category: str) -> str:
    lines = [f"Mình gợi ý top {len(products)} sản phẩm trong danh mục {category}:"]
    for idx, row in enumerate(products.itertuples(index=False), start=1):
        brand = getattr(row, "brand", "")
        brand_text = f" - {brand}" if brand and not pd.isna(brand) else ""
        rating = getattr(row, "rating_average", 0)
        reviews = int(getattr(row, "review_count", 0) or 0)
        lines.append(
            f"{idx}. {getattr(row, 'name', 'Sản phẩm Tiki')}{brand_text}\n"
            f"   Giá: {format_price(getattr(row, 'price', None))} | {rating}/5, {reviews} đánh giá\n"
            f"   Link: {getattr(row, 'product_url', '')}"
        )
    return "\n".join(lines)


def products_payload(products: pd.DataFrame) -> List[dict]:
    """Build JSON-safe product cards for frontend chat rendering."""
    payload: List[dict] = []
    for row in products.itertuples(index=False):
        price = pd.to_numeric(getattr(row, "price", None), errors="coerce")
        rating = pd.to_numeric(getattr(row, "rating_average", None), errors="coerce")
        review_count = pd.to_numeric(getattr(row, "review_count", None), errors="coerce")
        payload.append(
            {
                "product_id": int(getattr(row, "product_id", 0) or 0),
                "name": str(getattr(row, "name", "Sản phẩm Tiki")),
                "brand": "" if pd.isna(getattr(row, "brand", "")) else str(getattr(row, "brand", "")),
                "price": None if pd.isna(price) else int(price),
                "price_text": format_price(getattr(row, "price", None)),
                "rating_average": None if pd.isna(rating) else float(rating),
                "review_count": 0 if pd.isna(review_count) else int(review_count),
                "thumbnail_url": "" if pd.isna(getattr(row, "thumbnail_url", "")) else str(getattr(row, "thumbnail_url", "")),
                "product_url": "" if pd.isna(getattr(row, "product_url", "")) else str(getattr(row, "product_url", "")),
            }
        )
    return payload


def slot_number(value: Any) -> Optional[float]:
    """Convert pandas/numpy numeric values to JSON-safe slot values."""
    if value is None or pd.isna(value):
        return None
    return float(value)


def slot_product_ids(values: pd.Series) -> List[int]:
    """Convert product ids to plain Python ints for Rasa event serialization."""
    ids: List[int] = []
    for value in values.tolist():
        try:
            ids.append(int(value))
        except (TypeError, ValueError):
            continue
    return ids
