"""
Recommendation service for the Tiki product-link flow.

Flow:
1. Receive a Tiki product URL.
2. Read the product name from local CSV by product_id when possible, otherwise
   crawl the public page title.
3. Use the BiLSTM category model from category_service to predict the base
   category. If the model is unavailable, fall back to CSV category/keywords.
4. Pick related categories from a small rule map.
5. Search products in those related categories by product-name similarity.

The ranking keeps product-name similarity as the main signal. Rating and review
count are only small tie-breakers.
"""

from __future__ import annotations

import math
import re
import unicodedata
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
import requests
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

try:
    from bs4 import BeautifulSoup
except Exception:
    BeautifulSoup = None


PRODUCTS_PATH = "app/model/model_recommend/tiki_products_info.csv"
REVIEWS_PATH = "app/model/model_recommend/tiki_reviews_category.csv"

DEFAULT_PER_CATEGORY = 5
MAX_TOTAL_PRODUCTS = 20
MIN_SIMILARITY = 0.015
MIN_LSTM_CONFIDENCE = 45.0


# Categories are normalized to lowercase, no accents.
COMPLEMENTARY_MAP: Dict[str, List[str]] = {
    "dien thoai may tinh bang": [
        "dien thoai may tinh bang",
        "thiet bi kts phu kien so",
        "balo va vali",
    ],
    "laptop may vi tinh linh kien": [
        "laptop may vi tinh linh kien",
        "thiet bi kts phu kien so",
        "balo va vali",
    ],
    "thiet bi kts phu kien so": [
        "thiet bi kts phu kien so",
        "laptop may vi tinh linh kien",
        "dien thoai may tinh bang",
    ],
    "nha sach tiki": [
        "nha sach tiki",
        "nha cua doi song",
    ],
    "may anh": [
        "may anh",
        "thiet bi kts phu kien so",
        "balo va vali",
    ],
    "dien tu dien lanh": [
        "dien tu dien lanh",
        "dien gia dung",
        "cham soc nha cua",
        "nha cua doi song",
    ],
    "dien gia dung": [
        "dien gia dung",
        "nha cua doi song",
        "cham soc nha cua",
    ],
    "nha cua doi song": [
        "nha cua doi song",
        "cham soc nha cua",
        "dien gia dung",
    ],
    "thoi trang nam": [
        "thoi trang nam",
        "giay dep nam",
        "tui thoi trang nam",
        "phu kien thoi trang",
        "dong ho va trang suc",
    ],
    "thoi trang nu": [
        "thoi trang nu",
        "giay dep nu",
        "tui vi nu",
        "phu kien thoi trang",
        "dong ho va trang suc",
        "lam dep suc khoe",
    ],
    "giay dep nam": ["giay dep nam", "thoi trang nam", "phu kien thoi trang"],
    "giay dep nu": ["giay dep nu", "thoi trang nu", "phu kien thoi trang"],
    "tui vi nu": ["tui vi nu", "thoi trang nu", "giay dep nu"],
    "tui thoi trang nam": ["tui thoi trang nam", "thoi trang nam", "giay dep nam"],
    "phu kien thoi trang": [
        "phu kien thoi trang",
        "thoi trang nam",
        "thoi trang nu",
        "dong ho va trang suc",
    ],
    "dong ho va trang suc": [
        "dong ho va trang suc",
        "phu kien thoi trang",
        "thoi trang nam",
        "thoi trang nu",
    ],
    "lam dep suc khoe": ["lam dep suc khoe", "bach hoa online"],
    "the thao da ngoai": [
        "the thao da ngoai",
        "giay dep nam",
        "giay dep nu",
        "balo va vali",
    ],
    "balo va vali": ["balo va vali", "thoi trang nam", "thoi trang nu"],
    "o to xe may xe dap": [
        "o to xe may xe dap",
        "thiet bi kts phu kien so",
        "the thao da ngoai",
    ],
    "do choi me be": ["do choi me be", "nha sach tiki", "bach hoa online"],
    "bach hoa online": ["bach hoa online", "nha cua doi song", "dien gia dung"],
    "cham soc nha cua": ["cham soc nha cua", "nha cua doi song", "dien gia dung"],
}


class _Cache:
    products_df: Optional[pd.DataFrame] = None
    pid_category: Optional[Dict[str, str]] = None
    tfidf_per_cat: Optional[Dict[str, Tuple[TfidfVectorizer, object, pd.DataFrame]]] = None


_cache = _Cache()


def _find_file(filename: str) -> Path:
    here = Path(__file__).resolve()
    for parent in list(here.parents)[:6] + [Path.cwd()]:
        candidate = parent / filename
        if candidate.exists():
            return candidate
    raise FileNotFoundError(f"Khong tim thay file: {filename}")


def _strip_accents(text: str) -> str:
    text = unicodedata.normalize("NFD", str(text or ""))
    text = "".join(ch for ch in text if unicodedata.category(ch) != "Mn")
    return text.replace("đ", "d").replace("Đ", "D")


def _normalize_text(text: str) -> str:
    text = _strip_accents(text).lower()
    text = re.sub(r"[^a-z0-9\s]+", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def _normalize_category_label(category: str) -> str:
    normalized = _normalize_text(category)
    aliases = {
        "nha sach": "nha sach tiki",
        "nha sach tiki": "nha sach tiki",
        "dien thoai": "dien thoai may tinh bang",
        "may tinh bang": "dien thoai may tinh bang",
        "dien thoai may tinh bang": "dien thoai may tinh bang",
        "laptop may vi tinh linh kien": "laptop may vi tinh linh kien",
        "thiet bi kts phu kien so": "thiet bi kts phu kien so",
        "o to xe may xe dap": "o to xe may xe dap",
    }
    return aliases.get(normalized, normalized)


def _extract_product_id(product_url: str) -> Optional[str]:
    match = re.search(r"p(\d+)(?:\.html)?", str(product_url or ""))
    return match.group(1) if match else None


def _native(value):
    if isinstance(value, np.generic):
        return value.item()
    if pd.isna(value):
        return ""
    return value


def _to_float(value, default: float = 0.0) -> float:
    try:
        return float(value)
    except Exception:
        return default


def _to_int(value, default: int = 0) -> int:
    try:
        return int(float(value))
    except Exception:
        return default


def _load_data() -> None:
    """Load products/reviews and build one TF-IDF index per category."""
    if _cache.products_df is not None:
        return

    products = pd.read_csv(_find_file(PRODUCTS_PATH), keep_default_na=False)
    products["product_id"] = products["product_id"].astype(str)

    for col in [
        "name",
        "brand",
        "seller",
        "short_description",
        "description",
        "thumbnail_url",
        "product_url",
    ]:
        if col not in products.columns:
            products[col] = ""
        products[col] = products[col].fillna("").astype(str)

    products["price"] = pd.to_numeric(products.get("price", 0), errors="coerce").fillna(0)
    products["rating_average"] = pd.to_numeric(
        products.get("rating_average", 0), errors="coerce"
    ).fillna(0)
    products["review_count"] = pd.to_numeric(
        products.get("review_count", 0), errors="coerce"
    ).fillna(0)

    reviews = pd.read_csv(
        _find_file(REVIEWS_PATH),
        usecols=["product_id", "category"],
        keep_default_na=False,
    )
    reviews["product_id"] = reviews["product_id"].astype(str)
    reviews["category_norm"] = reviews["category"].apply(_normalize_category_label)
    reviews = reviews.drop_duplicates("product_id")

    pid_category = dict(zip(reviews["product_id"], reviews["category_norm"]))
    products["category_norm"] = products["product_id"].map(pid_category).fillna("")

    # Product name is the primary search document. Brand is included because
    # users often expect iPhone/Samsung/Logitech-like names to stay close.
    products["match_text"] = (
        products["name"].fillna("")
        + " "
        + products["brand"].fillna("")
    ).apply(_normalize_text)

    tfidf_per_cat: Dict[str, Tuple[TfidfVectorizer, object, pd.DataFrame]] = {}
    for category, sub_df in products.groupby("category_norm"):
        if not category:
            continue

        sub_df = sub_df.reset_index(drop=True).copy()
        texts = sub_df["match_text"].tolist()
        if not any(texts):
            continue

        vectorizer = TfidfVectorizer(
            analyzer="char_wb",
            ngram_range=(3, 5),
            min_df=1,
            sublinear_tf=True,
            norm="l2",
        )
        try:
            matrix = vectorizer.fit_transform(texts)
        except ValueError:
            continue

        tfidf_per_cat[category] = (vectorizer, matrix, sub_df)

    _cache.products_df = products
    _cache.pid_category = pid_category
    _cache.tfidf_per_cat = tfidf_per_cat


def _get_product_from_csv(product_url: str) -> Dict[str, str]:
    _load_data()
    assert _cache.products_df is not None

    product_id = _extract_product_id(product_url)
    row = pd.DataFrame()

    if product_id:
        row = _cache.products_df[_cache.products_df["product_id"] == product_id]

    if row.empty and product_url:
        row = _cache.products_df[
            _cache.products_df["product_url"].astype(str).str.contains(product_url, regex=False)
        ]

    if row.empty:
        return {}

    item = row.iloc[0]
    return {
        "product_id": str(item.get("product_id", "")),
        "title": str(item.get("name", "")),
        "description": str(item.get("short_description", "")),
        "category": str(item.get("category_norm", "")),
        "product_url": str(item.get("product_url", "")) or product_url,
    }


def _crawl_tiki(product_url: str) -> Dict[str, str]:
    if BeautifulSoup is None:
        return {
            "product_id": _extract_product_id(product_url) or "",
            "title": "",
            "description": "",
            "category": "",
            "product_url": product_url,
        }

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 Chrome/126.0.0.0 Safari/537.36"
        ),
        "Accept-Language": "vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7",
        "Referer": "https://tiki.vn/",
    }

    try:
        response = requests.get(product_url, headers=headers, timeout=12)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        title_tag = soup.find("meta", property="og:title") or soup.find("h1")
        title = ""
        if title_tag:
            title = (title_tag.get("content") or title_tag.get_text()).strip()

        desc_tag = (
            soup.find("meta", property="og:description")
            or soup.find("meta", attrs={"name": "description"})
        )
        description = desc_tag.get("content", "").strip() if desc_tag else ""
        return {
            "product_id": _extract_product_id(product_url) or "",
            "title": title,
            "description": description,
            "category": "",
            "product_url": product_url,
        }
    except Exception:
        return {
            "product_id": _extract_product_id(product_url) or "",
            "title": "",
            "description": "",
            "category": "",
            "product_url": product_url,
        }


def _classify_keyword(text: str) -> str:
    text = _normalize_text(text)
    rules = [
        (
            ["iphone", "ipad", "dien thoai", "smartphone", "samsung", "xiaomi", "oppo"],
            "dien thoai may tinh bang",
        ),
        (
            ["laptop", "macbook", "may tinh", "ban phim", "chuot", "ram", "ssd", "hdd"],
            "laptop may vi tinh linh kien",
        ),
        (
            ["tai nghe", "headphone", "loa", "cap", "sac", "hub", "usb", "webcam"],
            "thiet bi kts phu kien so",
        ),
        (["sach", "truyen", "tieu thuyet", "manga"], "nha sach tiki"),
        (["may anh", "camera", "canon", "nikon"], "may anh"),
        (["tivi", "tu lanh", "may giat", "dieu hoa", "may lanh"], "dien tu dien lanh"),
        (["noi", "bep", "may xay", "am dun"], "dien gia dung"),
        (["giay nam", "sneaker nam"], "giay dep nam"),
        (["giay nu", "sandal", "cao got"], "giay dep nu"),
        (["ao nu", "vay", "dam"], "thoi trang nu"),
        (["ao nam", "quan nam"], "thoi trang nam"),
        (["tui nu", "vi nu"], "tui vi nu"),
        (["tui nam", "vi nam"], "tui thoi trang nam"),
        (["balo", "vali"], "balo va vali"),
        (["dong ho", "smartwatch", "trang suc"], "dong ho va trang suc"),
        (["my pham", "kem duong", "son moi", "nuoc hoa"], "lam dep suc khoe"),
        (["the thao", "da ngoai", "outdoor"], "the thao da ngoai"),
        (["xe dap", "xe may", "o to"], "o to xe may xe dap"),
        (["do choi", "tre em", "be"], "do choi me be"),
        (["thuc pham", "do an", "nuoc uong"], "bach hoa online"),
        (["lau nha", "choi", "don dep"], "cham soc nha cua"),
        (["den", "ke", "noi that", "decor"], "nha cua doi song"),
    ]

    for keywords, category in rules:
        if any(keyword in text for keyword in keywords):
            return category

    return "bach hoa online"


def _predict_base_category(title: str, description: str, fallback_category: str) -> Tuple[str, float, str]:
    """Use the BiLSTM model first; fall back only when it cannot run."""
    model_text = " ".join(part for part in [title, description] if part).strip()

    if model_text:
        try:
            from app.services.category_service import predict_category

            category, confidence = predict_category(model_text)
            category = _normalize_category_label(category)
            confidence = float(confidence)
            if confidence >= MIN_LSTM_CONFIDENCE or not fallback_category:
                return category, confidence, "bilstm"
        except Exception:
            pass

    if fallback_category:
        return _normalize_category_label(fallback_category), 0.0, "csv"

    return _classify_keyword(model_text), 0.0, "keyword"


def _related_categories(base_category: str) -> List[str]:
    base_category = _normalize_category_label(base_category)
    categories = COMPLEMENTARY_MAP.get(base_category, [base_category])

    # Keep order while removing duplicates and unknown empty categories.
    result = []
    for category in categories:
        normalized = _normalize_category_label(category)
        if normalized and normalized not in result:
            result.append(normalized)
    return result


def extract_keywords(product_name: str, max_terms: int = 6) -> List[str]:
    """Small keyword list for display/debugging, not for hard filtering."""
    normalized = _normalize_text(product_name)
    stopwords = {
        "hang",
        "chinh",
        "hang chinh",
        "hang chinh hang",
        "bao",
        "hanh",
        "moi",
        "fullbox",
        "nhap",
        "khau",
        "tiki",
    }
    tokens = [tok for tok in normalized.split() if len(tok) > 1 and tok not in stopwords]
    keywords: List[str] = []
    for token in tokens:
        if token not in keywords:
            keywords.append(token)
        if len(keywords) >= max_terms:
            break
    return keywords


def _product_to_dict(row: pd.Series, category: str, similarity: float, score: float) -> Dict:
    return {
        "product_id": str(_native(row.get("product_id", ""))),
        "name": str(_native(row.get("name", ""))),
        "price": int(_to_int(row.get("price", 0))),
        "rating": round(_to_float(row.get("rating_average", 0)), 2),
        "review_count": _to_int(row.get("review_count", 0)),
        "brand": str(_native(row.get("brand", ""))),
        "thumbnail_url": str(_native(row.get("thumbnail_url", ""))),
        "product_url": str(_native(row.get("product_url", ""))),
        "category": category,
        "similarity": round(float(similarity), 4),
        "score": round(float(score), 4),
    }


def _search_in_category(
    query_name: str,
    category: str,
    top_k: int = DEFAULT_PER_CATEGORY,
    exclude_product_id: Optional[str] = None,
) -> List[Dict]:
    """Find products in a category using product-name similarity."""
    _load_data()
    assert _cache.tfidf_per_cat is not None

    category = _normalize_category_label(category)
    tfidf_data = _cache.tfidf_per_cat.get(category)
    if tfidf_data is None:
        return []

    vectorizer, matrix, sub_df = tfidf_data
    query = _normalize_text(query_name)
    if not query:
        return []

    try:
        q_vec = vectorizer.transform([query])
        similarities = cosine_similarity(q_vec, matrix).flatten()
    except Exception:
        return []

    ratings = sub_df["rating_average"].astype(float).clip(lower=0, upper=5).to_numpy()
    review_counts = sub_df["review_count"].astype(float).clip(lower=0).to_numpy()
    review_signal = np.log1p(review_counts) / max(1.0, math.log1p(float(review_counts.max() or 1)))

    # Name similarity is deliberately dominant. Quality only breaks ties.
    final_scores = similarities * 0.86 + (ratings / 5.0) * 0.09 + review_signal * 0.05

    order = final_scores.argsort()[::-1]
    results: List[Dict] = []
    for idx in order:
        row = sub_df.iloc[int(idx)]
        product_id = str(row.get("product_id", ""))
        if exclude_product_id and product_id == str(exclude_product_id):
            continue
        if similarities[idx] < MIN_SIMILARITY:
            continue

        results.append(
            _product_to_dict(
                row=row,
                category=category,
                similarity=float(similarities[idx]),
                score=float(final_scores[idx]),
            )
        )
        if len(results) >= top_k:
            break

    return results


def recommend_product(product_url: str, per_cat: int = DEFAULT_PER_CATEGORY) -> Dict:
    """Return related product suggestions for one Tiki product URL."""
    _load_data()

    product_url = str(product_url or "").strip()
    source = _get_product_from_csv(product_url)
    if not source:
        source = _crawl_tiki(product_url)

    title = source.get("title", "").strip()
    description = source.get("description", "").strip()
    product_id = source.get("product_id") or _extract_product_id(product_url) or ""

    if not title:
        raise ValueError("Khong lay duoc ten san pham tu link Tiki")

    base_category, confidence, model_name = _predict_base_category(
        title=title,
        description=description,
        fallback_category=source.get("category", ""),
    )
    related_categories = _related_categories(base_category)

    suggestions = []
    total = 0
    for category in related_categories:
        remaining = max(0, MAX_TOTAL_PRODUCTS - total)
        if remaining <= 0:
            break

        products = _search_in_category(
            query_name=title,
            category=category,
            top_k=min(per_cat, remaining),
            exclude_product_id=product_id,
        )
        if not products:
            continue

        suggestions.append({"category": category, "products": products})
        total += len(products)

    return {
        "input": {
            "product_url": product_url,
            "product_id": product_id,
            "title": title,
            "keywords": extract_keywords(title),
            "base_category": base_category,
            "category_confidence": round(confidence, 2),
            "category_model": model_name,
            "related_categories": related_categories,
            # Kept for backward compatibility with the old frontend.
            "complementary_categories": related_categories,
        },
        "suggestions": suggestions,
    }


def _print_result(result: Dict) -> None:
    input_data = result["input"]
    print("=" * 80)
    print(f"Product : {input_data['title']}")
    print(f"Category: {input_data['base_category']} ({input_data['category_model']})")
    print(f"Related : {', '.join(input_data['related_categories'])}")
    print("=" * 80)
    for group in result["suggestions"]:
        print(f"\n[{group['category']}]")
        for product in group["products"]:
            print(
                f"- {product['name'][:80]} | "
                f"sim={product['similarity']:.3f} | "
                f"rating={product['rating']} | "
                f"reviews={product['review_count']}"
            )


if __name__ == "__main__":
    demo_url = "https://tiki.vn/laptop-asus-vivobook-15-p12345678.html"
    _print_result(recommend_product(demo_url))
