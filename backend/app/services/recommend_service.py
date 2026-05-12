"""
recommend_service.py
====================
Luồng gợi ý sản phẩm bổ sung:

  Link Tiki
    → crawl tên sản phẩm
    → trích 1-2 keyword chính (VD: "laptop asus 8gb" → "laptop")
    → BiLSTM phân loại category (fallback: keyword classifier)
    → lấy category bổ sung từ bảng rule
    → với MỖI category: tìm top 1-2 sản phẩm tương đồng nhất
       bằng TF-IDF cosine similarity trên keyword
    → ghép + re-rank → trả về kết quả đa dạng

Yêu cầu:
    pip install scikit-learn pandas numpy requests beautifulsoup4
    (tuỳ chọn) pip install tensorflow joblib  ← cho BiLSTM
"""

import re
import os
import joblib
import requests
import numpy as np
import pandas as pd
from pathlib import Path
from bs4 import BeautifulSoup
from typing import List, Dict, Optional, Tuple
# use the new category service (BiLSTM)
from app.services.category_service import predict_category
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# ── BiLSTM (tuỳ chọn) ───────────────────────────────────────
try:
    from tensorflow.keras.models import load_model
    from tensorflow.keras.preprocessing.sequence import pad_sequences
    _TF_OK = True
except Exception:
    _TF_OK = False

# ─────────────────────────────────────────────
# CẤU HÌNH
# ─────────────────────────────────────────────
PRODUCTS_PATH = "tiki_products_info.csv"
REVIEWS_PATH  = "tiki_reviews_category.csv"
MAX_SEQ_LEN   = 100
PER_CAT_TOP_K = 2    # số sản phẩm lấy mỗi category bổ sung

CATEGORY_LABELS = [
    "nha cua doi song", "nha sach tiki", "dien thoai may tinh bang",
    "do choi me be", "thiet bi kts phu kien so", "dien gia dung",
    "lam dep suc khoe", "o to xe may xe dap", "thoi trang nu",
    "bach hoa online", "the thao da ngoai", "thoi trang nam",
    "laptop may vi tinh linh kien", "giay dep nam", "dien tu dien lanh",
    "giay dep nu", "may anh", "phu kien thoi trang", "dong ho va trang suc",
    "balo va vali", "tui vi nu", "tui thoi trang nam", "cham soc nha cua",
]

COMPLEMENTARY_MAP = {
    "laptop may vi tinh linh kien": [
        "thiet bi kts phu kien so",   # chuột, bàn phím, tai nghe, hub
        "balo va vali",               # túi, balo laptop
        "dong ho va trang suc",
        "laptop may vi tinh linh kien",# smartwatch
    ],
    "dien thoai may tinh bang": [
        "thiet bi kts phu kien so",   # ốp lưng, sạc, cáp, tai nghe
        "dong ho va trang suc",       # smartwatch
        "balo va vali", 
        "dien thoai may tinh bang",# túi đựng
    ],
    "may anh": [
        "thiet bi kts phu kien so",   # thẻ nhớ, pin, đèn flash
        "balo va vali",               # túi máy ảnh
        "may anh",
    ],
    "thiet bi kts phu kien so": [
        "laptop may vi tinh linh kien",
        "dien thoai may tinh bang",
        "thiet bi kts phu kien so",
    ],
    "dien tu dien lanh": [
        "dien gia dung",
        "cham soc nha cua",
        "nha cua doi song",
        "dien tu dien lanh",
    ],
    "dien gia dung": [
        "nha cua doi song",
        "cham soc nha cua",
        "bach hoa online",
        "dien gia dung",
    ],
    "nha cua doi song": [
        "cham soc nha cua",
        "dien gia dung",
        "bach hoa online",
        "nha cua doi song",
    ],
    "cham soc nha cua": [
        "nha cua doi song",
        "dien gia dung",
        "bach hoa online",
        "cham soc nha cua",
    ],
    "thoi trang nam": [
        "giay dep nam",
        "tui thoi trang nam",
        "dong ho va trang suc",
        "phu kien thoi trang",
        "thoi trang nam",
    ],
    "giay dep nam": [
        "thoi trang nam",
        "phu kien thoi trang",
        "giay dep nam",
    ],
    "tui thoi trang nam": [
        "thoi trang nam",
        "giay dep nam",
        "dong ho va trang suc",
        "tui thoi trang nam",
    ],
    "thoi trang nu": [
        "giay dep nu",
        "tui vi nu",
        "dong ho va trang suc",
        "phu kien thoi trang",
        "lam dep suc khoe",
        "thoi trang nu",
    ],
    "giay dep nu": [
        "thoi trang nu",
        "tui vi nu",
        "phu kien thoi trang",
        "giay dep nu",
    ],
    "tui vi nu": [
        "thoi trang nu",
        "giay dep nu",
        "dong ho va trang suc",
        "tui vi nu",
    ],
    "phu kien thoi trang": [
        "thoi trang nam",
        "thoi trang nu",
        "dong ho va trang suc",
        "phu kien thoi trang",
    ],
    "dong ho va trang suc": [
        "thoi trang nam",
        "thoi trang nu",
        "phu kien thoi trang",
        "dong ho va trang suc",
    ],
    "lam dep suc khoe": [
        "bach hoa online",
        "thoi trang nu",
        "cham soc nha cua",
        "lam dep suc khoe",
    ],
    "the thao da ngoai": [
        "giay dep nam",
        "giay dep nu",
        "balo va vali",
        "dong ho va trang suc",
        "the thao da ngoai",
    ],
    "balo va vali": [
        "thoi trang nam",
        "thoi trang nu",
        "the thao da ngoai",
        "balo va vali",
    ],
    "o to xe may xe dap": [
        "thiet bi kts phu kien so",   # camera hành trình, GPS
        "the thao da ngoai",          # đồ bảo hộ
        "balo va vali",
        "o to xe may xe dap",
    ],
    "do choi me be": [
        "nha sach tiki",
        "bach hoa online",
        "lam dep suc khoe",
        "do choi me be",
    ],
    "nha sach tiki": [
        "do choi me be",
        "balo va vali",
        "nha sach tiki"
    ],
    "bach hoa online": [
        "nha cua doi song",
        "dien gia dung",
        "lam dep suc khoe",
        "bach hoa online",
    ],
}

# ─────────────────────────────────────────────
# KEYWORD CHÍNH — ánh xạ category → từ khoá tìm kiếm ngữ nghĩa
# Dùng để tìm trong pool: "chuột laptop" tốt hơn "laptop asus 8gb viber..."
# ─────────────────────────────────────────────
CATEGORY_SEARCH_KEYWORDS = {
    "thiet bi kts phu kien so": [
        "chuột máy tính", "bàn phím", "tai nghe", "hub usb",
        "sạc laptop", "cáp", "webcam", "đế tản nhiệt",
    ],
    "balo va vali": [
        "túi laptop", "balo laptop", "túi chống sốc", "balo du lịch",
    ],
    "dong ho va trang suc": [
        "đồng hồ thông minh", "smartwatch", "đồng hồ nam", "đồng hồ nữ",
    ],
    "giay dep nam": ["giày nam", "giày thể thao nam", "dép nam"],
    "giay dep nu":  ["giày nữ", "giày cao gót", "dép nữ"],
    "thoi trang nam": ["áo nam", "quần nam", "áo thun nam"],
    "thoi trang nu":  ["áo nữ", "váy", "đầm", "áo thun nữ"],
    "tui vi nu":        ["túi xách nữ", "ví nữ", "clutch"],
    "tui thoi trang nam": ["túi nam", "ví nam", "túi đeo chéo"],
    "phu kien thoi trang": ["thắt lưng", "kính mắt", "mũ", "khăn"],
    "lam dep suc khoe":    ["kem dưỡng da", "son môi", "nước hoa", "mỹ phẩm"],
    "dien gia dung":   ["nồi cơm điện", "máy xay sinh tố", "bếp điện"],
    "nha cua doi song":  ["đèn trang trí", "kệ sách", "đồ nội thất"],
    "cham soc nha cua":  ["nước lau sàn", "chổi quét nhà", "khăn lau"],
    "bach hoa online":   ["thực phẩm", "đồ ăn vặt", "nước uống"],
    "the thao da ngoai": ["giày thể thao", "bình nước thể thao", "áo thể thao"],
    "may anh":           ["thẻ nhớ", "pin máy ảnh", "túi máy ảnh"],
    "do choi me be":     ["đồ chơi trẻ em", "sách thiếu nhi", "bỉm tã"],
    "nha sach tiki":     ["sách văn học", "sách kỹ năng", "truyện tranh"],
    "dien tu dien lanh": ["nước tẩy tủ lạnh", "phụ kiện máy giặt"],
    "o to xe may xe dap": ["camera hành trình", "mũ bảo hiểm", "bơm xe"],
    "dien thoai may tinh bang": ["ốp lưng", "tai nghe bluetooth", "sạc dự phòng"],
    "laptop may vi tinh linh kien": ["chuột không dây", "bàn phím cơ", "tai nghe gaming"],
}


# ─────────────────────────────────────────────
# CACHE
# ─────────────────────────────────────────────
class _Cache:
    bilstm    = None
    tokenizer = None
    products_df   : Optional[pd.DataFrame] = None
    pid_category  : Optional[Dict]         = None  # {product_id: category}
    cat_products  : Optional[Dict]         = None  # {category: [product_ids]}
    tfidf_per_cat : Optional[Dict]         = None  # {category: (vectorizer, matrix, ids)}

_cache = _Cache()


def _normalize_category_label(category: str) -> str:
    """Chuẩn hóa label category để tra rule map ổn định."""
    normalized = re.sub(r"\s+", " ", str(category or "")).strip().lower()
    alias_map = {
        "nha sach tiki": "nha sach tiki",
        "nhà sách tiki": "nha sach tiki",
        "nha sach": "nha sach tiki",
        "o to xe may xe dap": "o to xe may xe dap",
        "ô tô xe máy xe đạp": "o to xe may xe dap",
    }
    return alias_map.get(normalized, normalized)


# ─────────────────────────────────────────────
# BƯỚC 0: LOAD DATA & BUILD TF-IDF PER CATEGORY
# ─────────────────────────────────────────────
def _load_data():
    """Load CSV và build TF-IDF vectorizer cho từng category — chạy 1 lần."""
    if _cache.products_df is not None:
        return

    # Load products
    products = pd.read_csv(_find_file(PRODUCTS_PATH), keep_default_na=False)
    products["product_id"] = products["product_id"].astype(str)
    products["name"]              = products["name"].fillna("")
    products["short_description"] = products["short_description"].fillna("")
    products["rating_average"]    = pd.to_numeric(products["rating_average"], errors="coerce").fillna(3.0)
    products["review_count"]      = pd.to_numeric(products["review_count"],   errors="coerce").fillna(0)
    _cache.products_df = products

    # Load reviews để lấy category cho mỗi product_id
    reviews = pd.read_csv(_find_file(REVIEWS_PATH),
                          usecols=["product_id", "category"],
                          keep_default_na=False)
    reviews["product_id"]    = reviews["product_id"].astype(str)
    reviews["category_norm"] = reviews["category"].str.strip().str.lower()
    reviews = reviews.drop_duplicates("product_id")

    _cache.pid_category = dict(zip(reviews["product_id"], reviews["category_norm"]))

    # Nhóm product_id theo category
    cat_products: Dict[str, List[str]] = {}
    for pid, cat in _cache.pid_category.items():
        cat_products.setdefault(cat, []).append(pid)
    _cache.cat_products = cat_products

    # Build TF-IDF vectorizer cho từng category
    tfidf_per_cat = {}
    for cat, pids in cat_products.items():
        sub = products[products["product_id"].isin(pids)].copy()
        if sub.empty:
            continue
        # Text = tên + mô tả ngắn
        texts = (sub["name"] + " " + sub["short_description"]).tolist()
        vec = TfidfVectorizer(
            ngram_range=(1, 2),
            max_features=5000,
            sublinear_tf=True,
        )
        try:
            matrix = vec.fit_transform(texts)
            tfidf_per_cat[cat] = (vec, matrix, sub["product_id"].tolist(), sub)
        except Exception:
            pass

    _cache.tfidf_per_cat = tfidf_per_cat


def _find_file(filename: str) -> Path:
    here = Path(__file__).resolve()
    for p in list(here.parents)[:6] + [Path.cwd()]:
        c = p / filename
        if c.exists():
            return c
    raise FileNotFoundError(f"Không tìm thấy file: {filename}")


def _native(value):
    """Convert numpy/pandas scalars to plain Python types for JSON encoding."""
    if isinstance(value, np.generic):
        return value.item()
    return value


# ─────────────────────────────────────────────
# BƯỚC 1: CRAWL LINK TIKI
# ─────────────────────────────────────────────
def _crawl_tiki(url: str) -> Dict[str, str]:
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 Chrome/126.0.0.0 Safari/537.36"
        ),
        "Accept-Language": "vi-VN,vi;q=0.9",
        "Referer": "https://tiki.vn/",
    }
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        tag = soup.find("meta", property="og:title") or soup.find("h1")
        title = (tag.get("content") or tag.get_text()).strip() if tag else ""

        desc_tag = (soup.find("meta", property="og:description")
                    or soup.find("meta", attrs={"name": "description"}))
        desc = desc_tag["content"].strip() if desc_tag and desc_tag.get("content") else ""
        return {"title": title, "description": desc}

    except Exception:
        # Fallback: tra CSV theo product_id
        m = re.search(r"p(\d+)(?:\.html)?", url)
        if m:
            pid = m.group(1)
            try:
                df = pd.read_csv(_find_file(PRODUCTS_PATH),
                                 dtype=str, keep_default_na=False)
                row = df[df["product_id"] == pid]
                if not row.empty:
                    r = row.iloc[0]
                    return {
                        "title": r.get("name", ""),
                        "description": r.get("short_description", ""),
                    }
            except Exception:
                pass
        return {"title": "", "description": ""}


# ─────────────────────────────────────────────
# BƯỚC 2: TRÍCH KEYWORD CHÍNH
# ─────────────────────────────────────────────

# Từ vô nghĩa cần loại bỏ khỏi keyword
_NOISE = {
    "gb", "tb", "mb", "ram", "rom", "ssd", "hdd", "inch", "cm", "mm",
    "w", "v", "hz", "ghz", "mhz", "mah", "pin", "phiên", "bản", "hàng",
    "chính", "hãng", "tặng", "kèm", "miễn", "phí", "combo", "set",
    "và", "của", "cho", "với", "trong", "ngoài",
    "to", "the", "a", "an", "or", "of",
}

# Từ khoá mô tả loại sản phẩm — ưu tiên lấy làm keyword
_PRODUCT_TYPE_HINTS = [
    "laptop", "máy tính", "notebook", "macbook",
    "điện thoại", "smartphone", "iphone", "samsung",
    "máy ảnh", "camera",
    "tai nghe", "headphone", "airpod",
    "chuột", "bàn phím", "keyboard", "mouse",
    "màn hình", "monitor",
    "tivi", "tủ lạnh", "máy giặt", "máy lạnh", "điều hòa",
    "nồi", "bếp", "máy xay",
    "giày", "dép", "sneaker",
    "áo", "quần", "váy", "đầm",
    "túi", "balo", "ví",
    "đồng hồ", "smartwatch",
    "sách", "truyện",
    "xe đạp", "xe máy",
    "mỹ phẩm", "kem", "son",
]


def extract_keywords(product_name: str) -> List[str]:
    """
    Trích 1-2 keyword chính từ tên sản phẩm.

    Ưu tiên theo thứ tự:
      1. Từ khoá loại sản phẩm đã biết (laptop, giày, túi...)
      2. Từ đầu tiên không phải noise (thường là brand/loại)

    Ví dụ:
        "Laptop ASUS VivoBook 15 8GB 512GB" → ["laptop", "asus"]
        "Áo thun nam basic oversize"        → ["áo", "nam"]
        "Tai nghe Bluetooth Sony WH-1000XM5" → ["tai nghe", "bluetooth"]
    """
    name_lower = product_name.lower()
    keywords = []

    # Ưu tiên 1: tìm từ khoá loại sản phẩm
    for hint in _PRODUCT_TYPE_HINTS:
        if hint in name_lower and hint not in keywords:
            keywords.append(hint)
            if len(keywords) >= 1:
                break

    # Ưu tiên 2: từ đầu tiên không phải noise, không phải số
    tokens = re.split(r"[\s\-/,\.\(\)\[\]]+", name_lower)
    for tok in tokens:
        if tok and tok not in _NOISE and not tok.isdigit() and len(tok) > 1:
            if tok not in keywords:
                keywords.append(tok)
            if len(keywords) >= 2:
                break

    return keywords[:2] if keywords else [name_lower.split()[0]]


# ─────────────────────────────────────────────
# BƯỚC 3: PHÂN LOẠI CATEGORY
# ─────────────────────────────────────────────
def _load_bilstm():
    if _cache.bilstm is not None or _cache.tokenizer is not None:
        return _cache.bilstm
    if not _TF_OK:
        return None

    root = Path(__file__).resolve().parents[1] / "modelcategory"
    model_path = root / "bilstm_category_model.h5"
    tok_paths  = [root / "tokenizer.pkl", root / "tokenizer.joblib"]

    if model_path.exists():
        try:
            _cache.bilstm = load_model(str(model_path))
        except Exception:
            pass

    for p in tok_paths:
        if p.exists():
            try:
                _cache.tokenizer = joblib.load(str(p))
                break
            except Exception:
                pass

    return _cache.bilstm


def _classify_bilstm(text: str) -> Optional[str]:
    model = _load_bilstm()
    if model is None or _cache.tokenizer is None:
        return None
    try:
        seq    = _cache.tokenizer.texts_to_sequences([text])
        padded = pad_sequences(seq, maxlen=MAX_SEQ_LEN)
        preds  = model.predict(padded, verbose=0)
        idx    = int(np.argmax(preds, axis=1)[0])
        return CATEGORY_LABELS[idx] if 0 <= idx < len(CATEGORY_LABELS) else None
    except Exception:
        return None


def _classify_keyword(text: str) -> str:
    """Fallback phân loại đơn giản bằng keyword matching."""
    t = text.lower()
    rules = [
        (["laptop", "notebook", "macbook", "asus", "dell", "lenovo", "msi"],
         "laptop may vi tinh linh kien"),
        (["điện thoại", "smartphone", "iphone", "samsung", "xiaomi", "oppo"],
         "dien thoai may tinh bang"),
        (["máy ảnh", "dslr", "mirrorless", "canon", "nikon"],
         "may anh"),
        (["tai nghe", "headphone", "chuột", "mouse", "bàn phím", "hub usb",
          "sạc", "cáp", "powerbank"],
         "thiet bi kts phu kien so"),
        (["tivi", "tủ lạnh", "máy giặt", "điều hòa", "máy lạnh"],
         "dien tu dien lanh"),
        (["nồi", "bếp", "máy xay", "ấm đun"],
         "dien gia dung"),
        (["giày nam", "giay nam", "sneaker nam"],          "giay dep nam"),
        (["giày nữ", "giay nu", "sandal", "cao gót"],      "giay dep nu"),
        (["áo nữ", "váy", "đầm", "ao nu"],                "thoi trang nu"),
        (["áo nam", "quần nam", "ao nam"],                 "thoi trang nam"),
        (["túi nữ", "ví nữ", "clutch", "tui nu"],         "tui vi nu"),
        (["túi nam", "ví nam", "tui nam"],                 "tui thoi trang nam"),
        (["balo", "vali", "ba lô"],                        "balo va vali"),
        (["đồng hồ", "smartwatch", "trang sức"],           "dong ho va trang suc"),
        (["mỹ phẩm", "kem dưỡng", "son môi", "nước hoa"], "lam dep suc khoe"),
        (["sách", "truyện", "tiểu thuyết"],                "nha sach tiki"),
        (["đồ chơi", "trẻ em", "bé"],                     "do choi me be"),
        (["thể thao", "dã ngoại", "outdoor"],              "the thao da ngoai"),
        (["xe đạp", "xe máy", "ô tô"],                    "o to xe may xe dap"),
        (["đèn", "kệ", "nội thất", "decor"],              "nha cua doi song"),
        (["lau nhà", "chổi", "dọn dẹp"],                  "cham soc nha cua"),
        (["thực phẩm", "đồ ăn", "nước uống"],             "bach hoa online"),
    ]
    for keywords, cat in rules:
        if any(k in t for k in keywords):
            return cat
    return "bach hoa online"


def classify_category(text: str) -> str:
    return _classify_bilstm(text) or _classify_keyword(text)


# ─────────────────────────────────────────────
# BƯỚC 4: TÌM SẢN PHẨM TƯƠNG ĐỒNG THEO TỪNG CATEGORY
# ─────────────────────────────────────────────
def _search_in_category(
    query: str,
    category: str,
    top_k: int = PER_CAT_TOP_K,
) -> List[Dict]:
    """
    Tìm top_k sản phẩm trong 1 category có độ tương đồng TF-IDF cao nhất
    với query (thường là keyword chính + search hint của category đó).

    Re-rank cuối bằng: sim × rating × log(review_count+1)
    """
    _load_data()
    tfidf_data = _cache.tfidf_per_cat.get(category)
    if tfidf_data is None:
        return []

    vec, matrix, pids, sub_df = tfidf_data

    try:
        q_vec  = vec.transform([query])
        scores = cosine_similarity(q_vec, matrix).flatten()
    except Exception:
        return []

    # Re-rank: sim × chất lượng sản phẩm
    ratings = sub_df["rating_average"].values
    counts  = sub_df["review_count"].values
    final   = scores * ratings * np.log1p(counts + 1)

    top_idx = final.argsort()[::-1][:top_k]
    results = []
    for i in top_idx:
        if scores[i] < 0.01:   # bỏ kết quả không liên quan
            continue
        row = sub_df.iloc[i]
        results.append({
            "product_id"   : str(_native(row["product_id"])),
            "name"         : str(_native(row["name"])),
            "price"        : str(_native(row.get("price", ""))),
            "rating"       : float(_native(row["rating_average"])),
            "review_count" : int(_native(row["review_count"])),
            "thumbnail_url": str(_native(row.get("thumbnail_url", ""))),
            "product_url"  : str(_native(row.get("product_url", ""))),
            "category"     : str(category),
            "similarity"   : float(round(float(scores[i]), 4)),
            "score"        : float(round(float(final[i]), 4)),
        })
    return results


# ─────────────────────────────────────────────
# HÀM CHÍNH
# ─────────────────────────────────────────────
def recommend_product(product_url: str, per_cat: int = PER_CAT_TOP_K) -> Dict:
    """
    Gợi ý sản phẩm bổ sung từ link Tiki.

    Args:
        product_url: URL sản phẩm Tiki
        per_cat:     Số sản phẩm lấy mỗi category bổ sung (mặc định 2)

    Returns:
        {
          "input": {
              "title": str,
              "keywords": List[str],
              "base_category": str,
              "complementary_categories": List[str],
          },
          "suggestions": [
              {
                  "category": str,
                  "products": [
                      {
                          "product_id", "name", "price",
                          "rating", "review_count",
                          "thumbnail_url", "product_url",
                          "similarity", "score"
                      }, ...
                  ]
              }, ...
          ]
        }
    """
    _load_data()

    # 1. Crawl tên sản phẩm
    scraped   = _crawl_tiki(product_url)
    title     = scraped.get("title", "")
    full_text = title + " " + scraped.get("description", "")

    # 2. Trích keyword chính
    keywords = extract_keywords(title) if title else ["sản phẩm"]

    # 3. Phân loại category — ưu tiên BiLSTM từ `category_service.predict_category`
    try:
        # predict_category returns (category, confidence)
        base_cat, confidence = predict_category(title or full_text)
    except Exception:
        base_cat = classify_category(full_text or title)

    base_cat = _normalize_category_label(base_cat)

    # 4. Lấy các category bổ sung
    comp_cats = COMPLEMENTARY_MAP.get(base_cat, [])

    # 5. Với mỗi category bổ sung: build query và tìm top sản phẩm
    suggestions = []
    for cat in comp_cats:
        # Query = keyword chính + hint tìm kiếm của category đó
        hints       = CATEGORY_SEARCH_KEYWORDS.get(cat, [])
        search_hint = hints[0] if hints else cat.replace(" ", " ")
        query       = " ".join(keywords) + " " + search_hint

        products_in_cat = _search_in_category(query, cat, top_k=per_cat)
        if products_in_cat:
            suggestions.append({
                "category": cat,
                "products": products_in_cat,
            })

    return {
        "input": {
            "title"                   : title,
            "keywords"                : [str(_native(k)) for k in keywords],
            "base_category"           : base_cat,
            "complementary_categories": [str(_native(c)) for c in comp_cats],
        },
        "suggestions": suggestions,
    }


# ─────────────────────────────────────────────
# DEMO
# ─────────────────────────────────────────────
def _print_result(result: Dict):
    inp = result["input"]
    print(f"\n{'='*60}")
    print(f"Sản phẩm : {inp['title']}")
    print(f"Keyword  : {inp['keywords']}")
    print(f"Category : {inp['base_category']}")
    print(f"Bổ sung  : {inp['complementary_categories']}")
    print(f"{'='*60}")
    for group in result["suggestions"]:
        print(f"\n▶ [{group['category']}]")
        for p in group["products"]:
            print(f"   • {p['name'][:65]}")
            print(f"     sim={p['similarity']:.3f} | ⭐{p['rating']} "
                  f"| {p['review_count']} reviews")


if __name__ == "__main__":
    # Test thử — thay bằng link thật hoặc test với product_id từ CSV
    test_url = "https://tiki.vn/laptop-asus-vivobook-15-p12345678.html"
    print(f"Test URL: {test_url}")
    result = recommend_product(test_url)
    _print_result(result)