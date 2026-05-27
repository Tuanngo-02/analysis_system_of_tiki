"""Build the FAISS product index for the Tiki Rasa chatbot.

Run from `backend/chatbot`:
    python build_index.py

The script reads product metadata and reviews, creates one rich Vietnamese
search document per product, encodes all products on CPU with Sentence-
Transformers, normalizes vectors, and stores a FAISS IndexFlatIP index. Because
vectors are normalized, inner product is cosine similarity.
"""

from __future__ import annotations

import os
import pickle
import re
from pathlib import Path
from typing import Any

import faiss
import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer


MODEL_NAME = os.getenv(
    "TIKI_EMBEDDING_MODEL", "bkai-foundation-models/vietnamese-bi-encoder"
)
BATCH_SIZE = int(os.getenv("TIKI_INDEX_BATCH_SIZE", "64"))

CHATBOT_DIR = Path(__file__).resolve().parent
REPO_ROOT = CHATBOT_DIR.parents[1]
DEFAULT_PRODUCTS_CSV = REPO_ROOT / "train_test" / "tiki_products_info.csv"
DEFAULT_REVIEWS_CSV = REPO_ROOT / "train_test" / "tiki_reviews_category.csv"
PRODUCTS_CSV = Path(os.getenv("TIKI_PRODUCTS_CSV", DEFAULT_PRODUCTS_CSV))
REVIEWS_CSV = Path(os.getenv("TIKI_REVIEWS_CSV", DEFAULT_REVIEWS_CSV))
OUTPUT_DIR = Path(os.getenv("TIKI_CHATBOT_INDEX_DIR", CHATBOT_DIR / "storage"))


def clean_text(value: Any) -> str:
    """Return compact text and remove HTML fragments from descriptions."""
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return ""
    text = re.sub(r"<[^>]+>", " ", str(value))
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def read_csv(path: Path) -> pd.DataFrame:
    """Read CSV with UTF-8 first, then UTF-8-SIG for exported Vietnamese files."""
    if not path.exists():
        raise FileNotFoundError(f"CSV not found: {path}")
    try:
        return pd.read_csv(path)
    except UnicodeDecodeError:
        return pd.read_csv(path, encoding="utf-8-sig")


def build_search_text(row: pd.Series) -> str:
    """Create the text that represents a product in semantic search."""
    parts = [
        f"Tên sản phẩm: {clean_text(row.get('name'))}",
        f"Danh mục: {clean_text(row.get('category'))}",
        f"Thương hiệu: {clean_text(row.get('brand'))}",
        f"Nhà bán: {clean_text(row.get('seller'))}",
        f"Mô tả ngắn: {clean_text(row.get('short_description'))}",
        f"Mô tả: {clean_text(row.get('description'))[:1500]}",
        f"Nhận xét khách hàng: {clean_text(row.get('review_summary'))[:800]}",
    ]
    return ". ".join(part for part in parts if part and not part.endswith(": "))


def prepare_products(products: pd.DataFrame, reviews: pd.DataFrame) -> pd.DataFrame:
    """Merge review category/text signals into product metadata."""
    required = {"product_id", "name", "price"}
    missing = required - set(products.columns)
    if missing:
        raise ValueError(f"Products CSV is missing required columns: {sorted(missing)}")

    products = products.copy()
    products["product_id"] = pd.to_numeric(products["product_id"], errors="coerce")
    products = products.dropna(subset=["product_id"]).drop_duplicates("product_id")
    products["product_id"] = products["product_id"].astype("int64")

    if not reviews.empty and "product_id" in reviews.columns:
        reviews = reviews.copy()
        reviews["product_id"] = pd.to_numeric(reviews["product_id"], errors="coerce")
        reviews = reviews.dropna(subset=["product_id"])
        reviews["product_id"] = reviews["product_id"].astype("int64")
        review_agg = (
            reviews.groupby("product_id")
            .agg(
                category=("category", lambda s: clean_text(s.dropna().mode().iloc[0]) if not s.dropna().empty else ""),
                review_summary=("review_text", lambda s: " ".join(clean_text(x) for x in s.dropna().head(8))),
            )
            .reset_index()
        )
        products = products.merge(review_agg, on="product_id", how="left")
    else:
        products["category"] = ""
        products["review_summary"] = ""

    products["category"] = products.get("category", "").fillna("")
    products["review_summary"] = products.get("review_summary", "").fillna("")

    for column in [
        "rating_average",
        "review_count",
        "price",
        "brand",
        "seller",
        "short_description",
        "description",
        "thumbnail_url",
        "product_url",
        "inventory_status",
    ]:
        if column not in products.columns:
            products[column] = "" if column not in {"rating_average", "review_count", "price"} else 0

    products["price"] = pd.to_numeric(products["price"], errors="coerce").fillna(0)
    products["rating_average"] = pd.to_numeric(
        products["rating_average"], errors="coerce"
    ).fillna(0)
    products["review_count"] = pd.to_numeric(products["review_count"], errors="coerce").fillna(0)
    products["search_text"] = products.apply(build_search_text, axis=1)
    products = products[products["search_text"].str.len() > 0].reset_index(drop=True)
    return products


def main() -> None:
    print(f"Reading products: {PRODUCTS_CSV}")
    products = read_csv(PRODUCTS_CSV)
    print(f"Reading reviews: {REVIEWS_CSV}")
    reviews = read_csv(REVIEWS_CSV) if REVIEWS_CSV.exists() else pd.DataFrame()

    products = prepare_products(products, reviews)
    print(f"Prepared {len(products):,} products for indexing.")

    model = SentenceTransformer(MODEL_NAME, device="cpu")
    embeddings = model.encode(
        products["search_text"].tolist(),
        batch_size=BATCH_SIZE,
        normalize_embeddings=True,
        convert_to_numpy=True,
        show_progress_bar=True,
    ).astype("float32")

    index = faiss.IndexFlatIP(embeddings.shape[1])
    index.add(np.ascontiguousarray(embeddings))

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    faiss.write_index(index, str(OUTPUT_DIR / "products.faiss"))
    with (OUTPUT_DIR / "products_metadata.pkl").open("wb") as file:
        pickle.dump(products, file)

    print(f"Saved FAISS index: {OUTPUT_DIR / 'products.faiss'}")
    print(f"Saved metadata: {OUTPUT_DIR / 'products_metadata.pkl'}")


if __name__ == "__main__":
    main()
