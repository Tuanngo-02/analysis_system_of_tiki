import os
from pathlib import Path
import re
import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
from gensim.models import Word2Vec, KeyedVectors
from typing import List, Dict

# Optional modern NLP imports (PhoBERT + BM25 hybrid)
try:
    import torch
    from transformers import AutoTokenizer, AutoModel
    from rank_bm25 import BM25Okapi
    from sklearn.preprocessing import MinMaxScaler
    from sklearn.metrics.pairwise import cosine_similarity
except Exception:
    torch = None
    AutoTokenizer = None
    AutoModel = None
    BM25Okapi = None
    MinMaxScaler = None
    cosine_similarity = None

# Try import keras if available for BiLSTM (optional)
try:
    from tensorflow.keras.models import load_model
    import joblib
except Exception:
    load_model = None


# Complementary rules (can be extended)
complementary_rules = {
    "nha cua doi song": ["cham soc nha cua", "bach hoa online", "dien gia dung","nha cua doi song"],
    "nha sach tiki": ["bach hoa online", "phu kien thoi trang","nha sach tiki"],
    "dien thoai may tinh bang": ["thiet bi kts phu kien so", "tai nghe", "balo va vali"],
    "do choi me be": ["thoi trang nu", "bach hoa online"],
    "thiet bi kts phu kien so": ["phu kien thoi trang", "balo va vali", "tai nghe"],
    "dien gia dung": ["cham soc nha cua", "bach hoa online"],
    "lam dep suc khoe": ["bach hoa online", "phu kien thoi trang"],
    "o to xe may xe dap": ["dong ho va trang suc", "phu kien thoi trang"],
    "thoi trang nu": ["phu kien thoi trang", "tui vi nu", "giay dep nu"],
    "bach hoa online": ["cham soc nha cua", "lam dep suc khoe"],
    "the thao da ngoai": ["balo va vali", "giay dep nam", "giay dep nu"],
    "thoi trang nam": ["phu kien thoi trang", "tui thoi trang nam", "giay dep nam"],
    "laptop may vi tinh linh kien": ["thiet bi kts phu kien so", "balo va vali", "phu kien thoi trang"],
    "giay dep nam": ["thoi trang nam", "phu kien thoi trang"],
    "dien tu dien lanh": ["dien gia dung", "bach hoa online"],
    "giay dep nu": ["thoi trang nu", "phu kien thoi trang", "tui vi nu"],
    "may anh": ["thiet bi kts phu kien so", "balo va vali", "phu kien thoi trang"],
    "phu kien thoi trang": ["tui vi nu", "tui thoi trang nam", "balo va vali"],
    "dong ho va trang suc": ["phu kien thoi trang", "tui vi nu"],
    "balo va vali": ["phu kien thoi trang", "tui thoi trang nam"],
    "tui vi nu": ["thoi trang nu", "phu kien thoi trang"],
    "tui thoi trang nam": ["thoi trang nam", "phu kien thoi trang"],
    "cham soc nha cua": ["nha cua doi song", "bach hoa online"],
}

# Category labels order (must match BiLSTM training label encoding)
# Adjust this list if your model used a different order.
CATEGORY_LABELS = [
    "nha cua doi song",
    "nha sach tiki",
    "dien thoai may tinh bang",
    "do choi me be",
    "thiet bi kts phu kien so",
    "dien gia dung",
    "lam dep suc khoe",
    "o to xe may xe dap",
    "thoi trang nu",
    "bach hoa online",
    "the thao da ngoai",
    "thoi trang nam",
    "laptop may vi tinh linh kien",
    "giay dep nam",
    "dien tu dien lanh",
    "giay dep nu",
    "may anh",
    "phu kien thoi trang",
    "dong ho va trang suc",
    "balo va vali",
    "tui vi nu",
    "tui thoi trang nam",
    "cham soc nha cua",
]

# Default max sequence length for tokenizer padding (match training maxlen if available)
MAX_SEQUENCE_LENGTH = 100


def _crawl_tiki_product(url: str) -> Dict[str, str]:
    """Fetch the product page and extract title + description via meta tags.

    Uses a browser-like User-Agent header. If the request is blocked (403),
    falls back to looking up the product in the local CSV by product id.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
        "Accept-Language": "vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7",
        "Referer": "https://tiki.vn/",
    }

    session = requests.Session()
    try:
        resp = session.get(url, headers=headers, timeout=10)
        if resp.status_code == 403:
            raise requests.exceptions.HTTPError(f"403 for {url}")
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        # prefer og:title and og:description
        title_tag = soup.find("meta", property="og:title") or soup.find("meta", attrs={"name": "title"})
        desc_tag = soup.find("meta", property="og:description") or soup.find("meta", attrs={"name": "description"})

        title = title_tag["content"].strip() if title_tag and title_tag.get("content") else ""
        description = desc_tag["content"].strip() if desc_tag and desc_tag.get("content") else ""

        # fallback try h1 and element with data-testid description
        if not title:
            h1 = soup.find("h1")
            title = h1.get_text(strip=True) if h1 else ""
        if not description:
            # try to collect short description
            short = soup.find(attrs={"data-widget": "short_description"}) or soup.find(class_=re.compile("short|desc", re.I))
            description = short.get_text(strip=True) if short else description

        return {"title": title, "description": description}
    except requests.exceptions.HTTPError:
        # try fallback: extract product id from url and lookup CSV
        pid = None
        m = re.search(r"p(\d+)\\.html", url)
        if not m:
            m = re.search(r"p(\d+)", url)
        if m:
            pid = m.group(1)
        if pid:
            # lookup CSV using robust finder
            csv_path = _find_csv("tiki_products_info.csv")
            if csv_path is not None:
                try:
                    df = pd.read_csv(csv_path, dtype=str, keep_default_na=False)
                    row = df[df["product_id"] == pid]
                    if not row.empty:
                        r = row.iloc[0]
                        return {"title": r.get("name", ""), "description": r.get("description", r.get("short_description", ""))}
                except Exception:
                    pass
        # final fallback: return empty strings
        return {"title": "", "description": ""}


def _simple_keyword_classifier(text: str) -> str:
    t = text.lower()

    # mapping of category -> keywords (case-insensitive)
    category_keywords = {
        "laptop may vi tinh linh kien": ["laptop", "notebook", "acer", "asus", "lenovo", "dell", "msi", "macbook"],
        "dien thoai may tinh bang": ["điện thoại", "dien thoai", "smartphone", "iphone", "samsung", "xiaomi", "oppo"],
        "may anh": ["máy ảnh", "may anh", "dslr", "mirrorless", "canon", "nikon", "sony"],
        "thiet bi kts phu kien so": ["tai nghe", "headphone", "headset", "chuột", "mouse", "sạc", "sac", "powerbank"],
        "phu kien thoi trang": ["phụ kiện thời trang", "phu kien thoi trang", "kính", "belt", "thắt lưng", "ví", "ví"],
        "balo va vali": ["balo", "vali", "backpack", "túi", "tui xach"],
        "tui vi nu": ["ví nữ", "vi nu", "wallet female"],
        "tui thoi trang nam": ["ví nam", "tui nam", "wallet male"],
        "giay dep nam": ["giày nam", "giay nam", "sneaker nam", "boots"],
        "giay dep nu": ["giày nữ", "giay nu", "sneaker nu", "heels", "sandals"],
        "thoi trang nu": ["áo nữ", "ao nu", "váy", "vay", "đầm", "dam"],
        "thoi trang nam": ["áo nam", "ao nam", "quần nam", "quan nam"],
        "dien tu dien lanh": ["tivi", "tủ lạnh", "tu lanh", "máy giặt", "may giat", "máy lạnh"],
        "dien gia dung": ["gia dụng", "nồi", "noi com", "bếp", "may xay"],
        "lam dep suc khoe": ["mỹ phẩm", "my pham", "skincare", "son", "nước hoa", "nuoc hoa"],
        "nha cua doi song": ["nha", "trang trí", "decor", "noi that", "noi thất"],
        "bach hoa online": ["tạp hóa", "tap hoa", "bach hoa", "tạp hóa online"],
        "cham soc nha cua": ["lau nhà", "don nhà", "dọn nhà", "clean"],
        "o to xe may xe dap": ["ô tô", "oto", "xe máy", "xe dap", "xe đạp"],
        "the thao da ngoai": ["thể thao", "the thao", "dã ngoại", "da ngoai", "outdoor"],
        "dong ho va trang suc": ["đồng hồ", "dong ho", "trang sức", "trang suc", "necklace"],
        "do choi me be": ["đồ chơi", "do choi", "bé", "me be", "trẻ em"],
        "may anh": ["máy ảnh", "may anh"],
    }

    for category, keys in category_keywords.items():
        if any(k in t for k in keys):
            return category

    # fallback: try to detect electronics broadly
    if any(k in t for k in ["pin", "sạc", "adapter", "usb", "điện tử"]):
        return "thiet bi kts phu kien so"

    # default fallback
    return "bach hoa online"


class ModelsCache:
    def __init__(self):
        self.w2v = None
        self.bilstm = None
        self.tokenizer = None
        self.phobert_tokenizer = None
        self.phobert_model = None
        self.phobert_device = None
        self.phobert_embeddings = None


_cache = ModelsCache()


def _load_bilstm():
    """Load BiLSTM model and tokenizer if available. Caches results in _cache.

    Returns the model object or None.
    """
    if _cache.bilstm is not None or _cache.tokenizer is not None:
        return _cache.bilstm

    app_root = Path(__file__).resolve().parents[1]
    model_path = app_root / "modelcategory" / "bilstm_category_model.h5"
    tok_paths = [
        app_root / "modelcategory" / "tokenizer.pkl",
        app_root / "modelcategory" / "tokenizer.joblib",
        app_root / "modelcategory" / "tokenizer.pkl.gz",
    ]

    # load model if possible
    if model_path.exists() and load_model is not None:
        try:
            _cache.bilstm = load_model(str(model_path))
        except Exception:
            _cache.bilstm = None

    # load tokenizer (try joblib/pickle)
    for p in tok_paths:
        if p.exists():
            try:
                _cache.tokenizer = joblib.load(str(p))
                break
            except Exception:
                try:
                    import pickle

                    with open(p, "rb") as f:
                        _cache.tokenizer = pickle.load(f)
                        break
                except Exception:
                    _cache.tokenizer = None

    return _cache.bilstm


def _ensure_phobert(model_name: str = "vinai/phobert-base"):
    """Load PhoBERT tokenizer and model into cache. Returns True if available."""
    if _cache.phobert_model is not None and _cache.phobert_tokenizer is not None:
        return True
    if AutoTokenizer is None or AutoModel is None or torch is None:
        return False

    app_root = Path(__file__).resolve().parents[1]
    # allow local model folder fallback if present
    local_model_path = app_root / "modelcategory" / "phobert"
    try:
        if local_model_path.exists():
            _cache.phobert_tokenizer = AutoTokenizer.from_pretrained(str(local_model_path))
            _cache.phobert_model = AutoModel.from_pretrained(str(local_model_path))
        else:
            _cache.phobert_tokenizer = AutoTokenizer.from_pretrained(model_name)
            _cache.phobert_model = AutoModel.from_pretrained(model_name)
        _cache.phobert_device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        _cache.phobert_model.to(_cache.phobert_device)
        _cache.phobert_model.eval()
        return True
    except Exception:
        _cache.phobert_model = None
        _cache.phobert_tokenizer = None
        _cache.phobert_device = None
        return False


def _load_phobert_embeddings():
    """Load precomputed PhoBERT embeddings (.npy) into cache if present."""
    if _cache.phobert_embeddings is not None:
        return True
    app_root = Path(__file__).resolve().parents[1]
    emb_path = app_root / "modelcategory" / "tiki_phobert_full_embeddings.npy"
    if emb_path.exists():
        try:
            _cache.phobert_embeddings = np.load(str(emb_path))
            return True
        except Exception:
            _cache.phobert_embeddings = None
            return False
    return False


def _phobert_text_embedding(text: str):
    """Return numpy vector embedding for text using PhoBERT mean pooling."""
    if not _ensure_phobert():
        return None
    tok = _cache.phobert_tokenizer
    model = _cache.phobert_model
    device = _cache.phobert_device
    try:
        inputs = tok(text, return_tensors="pt", truncation=True, max_length=256)
        inputs = {k: v.to(device) for k, v in inputs.items()}
        with torch.no_grad():
            outputs = model(**inputs)
        # mean pooling on last hidden state
        emb = outputs.last_hidden_state.mean(dim=1).cpu().numpy()[0]
        return emb
    except Exception:
        return None


def _load_w2v():
    if _cache.w2v is not None:
        return _cache.w2v
    app_root = Path(__file__).resolve().parents[1]
    w2v_path = app_root / "modelcategory" / "tiki_word2vec.model"
    if w2v_path.exists():
        try:
            loaded = KeyedVectors.load(str(w2v_path), mmap='r')
            # if loaded is a wrapper with .wv, use that; otherwise assume it's KeyedVectors
            _cache.w2v = loaded.wv if hasattr(loaded, "wv") else loaded
        except Exception:
            # gensim Word2Vec format fallback
            loaded = Word2Vec.load(str(w2v_path))
            # Word2Vec has `.wv` (KeyedVectors); expose that for membership and vector lookup
            _cache.w2v = loaded.wv
    return _cache.w2v


def _text_to_vector(text: str):
    w2v = _load_w2v()
    if w2v is None:
        return np.zeros(100, dtype=float)
    words = re.findall(r"\w+", text.lower())
    vecs = []
    for w in words:
        try:
            vecs.append(w2v[w])
        except Exception:
            continue
    if not vecs:
        try:
            sz = int(getattr(w2v, "vector_size", 100))
        except Exception:
            sz = 100
        return np.zeros(sz, dtype=float)
    return np.mean(vecs, axis=0)


def _cosine(a: np.ndarray, b: np.ndarray) -> float:
    if a is None or b is None:
        return 0.0
    na = np.linalg.norm(a)
    nb = np.linalg.norm(b)
    if na == 0 or nb == 0:
        return 0.0
    return float(np.dot(a, b) / (na * nb))


def _expand_categories(base_cat: str) -> List[str]:
    extras = complementary_rules.get(base_cat, [])
    return [base_cat] + extras


def _find_csv(filename: str) -> Path:
    """Search up from this file's directory and cwd for the given filename."""
    here = Path(__file__).resolve()
    # check current file parents up to 5 levels
    for p in list(here.parents)[:6]:
        candidate = p / filename
        if candidate.exists():
            return candidate
    # check cwd
    cwd_candidate = Path.cwd() / filename
    if cwd_candidate.exists():
        return cwd_candidate
    # not found
    return None


def recommend_product(product_url: str, top_k: int = 5) -> Dict:
    # 1. Crawl product
    scraped = _crawl_tiki_product(product_url)
    title = scraped.get("title", "")
    description = scraped.get("description", "")
    full_text = (title + " ") + (description or "")

    # 2. Classify (try BiLSTM model; fallback to simple keyword)
    base_category = None
    try:
        bilstm = _load_bilstm()
        if bilstm is not None and _cache.tokenizer is not None:
            # lazy import pad_sequences
            try:
                from tensorflow.keras.preprocessing.sequence import pad_sequences
            except Exception:
                pad_sequences = None

            if pad_sequences is not None:
                try:
                    seq = _cache.tokenizer.texts_to_sequences([full_text])
                    padded = pad_sequences(seq, maxlen=MAX_SEQUENCE_LENGTH)
                    preds = bilstm.predict(padded)
                    idx = int(np.argmax(preds, axis=1)[0])
                    if 0 <= idx < len(CATEGORY_LABELS):
                        base_category = CATEGORY_LABELS[idx]
                except Exception:
                    base_category = None

    except Exception:
        base_category = None

    if base_category is None:
        base_category = _simple_keyword_classifier(full_text)

    # 3. Expand via rules
    categories = _expand_categories(base_category)

    # 4. Load products CSV and build candidate pool
    csv_path = _find_csv("tiki_products_info.csv")
    if csv_path is None:
        raise FileNotFoundError("CSV database not found: tiki_products_info.csv (searched parents and cwd)")
    df = pd.read_csv(csv_path, dtype=str, keep_default_na=False)

    # build keyword list from categories (split words)
    keywords = set()
    for c in categories:
        for w in re.findall(r"\w+", c.lower()):
            keywords.add(w)

    # filter rows where any keyword appears in name or description
    def row_matches(row):
        hay = (row.get("name", "") + " " + row.get("short_description", "") + " " + row.get("description", "")).lower()
        return any(k in hay for k in keywords)

    try:
        candidates = df[df.apply(row_matches, axis=1)]
    except Exception:
        candidates = df

    # limit candidate set to reasonable size
    if len(candidates) > 5000:
        candidates = candidates.sample(5000, random_state=42)


    # 5. Retrieve candidate texts
    candidate_texts = []
    for _, r in candidates.iterrows():
        text = (r.get("name", "") + " ") + (r.get("short_description", "") or r.get("description", ""))
        candidate_texts.append(text)

    results = []

    # Try PhoBERT + BM25 hybrid if available
    phobert_ready = _ensure_phobert()
    bm25 = None
    bert_matrix = None
    if BM25Okapi is not None and len(candidate_texts) > 0:
        tokenized_corpus = [t.split() for t in candidate_texts]
        try:
            bm25 = BM25Okapi(tokenized_corpus)
        except Exception:
            bm25 = None

    # Try load precomputed embeddings first
    emb_loaded = _load_phobert_embeddings()
    if emb_loaded and _cache.phobert_embeddings is not None:
        try:
            # select rows matching candidates' original CSV positions
            idx = candidates.index.to_numpy().astype(int)
            bert_matrix = _cache.phobert_embeddings[idx]
        except Exception:
            bert_matrix = None
    else:
        if phobert_ready:
            embs = []
            for t in candidate_texts:
                e = _phobert_text_embedding(t)
                if e is None:
                    # fallback to zero vector
                    e = np.zeros(768, dtype=float)
                embs.append(e)
            try:
                bert_matrix = np.vstack(embs)
            except Exception:
                bert_matrix = None
        else:
            bert_matrix = None

    if bert_matrix is not None and bm25 is not None and MinMaxScaler is not None and cosine_similarity is not None:
        # Hybrid retrieval. Compute query embedding if model available, else BM25-only.
        processed_query = (title + " " + (description or "")).strip()
        query_tokens = processed_query.split()

        q_emb = None
        if _cache.phobert_model is not None and _cache.phobert_tokenizer is not None:
            q_emb = _phobert_text_embedding(processed_query)

        if q_emb is None:
            # Fall back to BM25-only scoring
            bm25_scores = bm25.get_scores(query_tokens)
            try:
                scaler = MinMaxScaler()
                bm25_scores_norm = scaler.fit_transform(np.array(bm25_scores).reshape(-1, 1)).flatten()
            except Exception:
                bm25_scores_norm = bm25_scores
            final_scores = bm25_scores_norm
        else:
            bert_sims = cosine_similarity(q_emb.reshape(1, -1), bert_matrix).flatten()
            bm25_scores = bm25.get_scores(query_tokens)
            # normalize
            try:
                scaler = MinMaxScaler()
                bert_scores_norm = scaler.fit_transform(bert_sims.reshape(-1, 1)).flatten()
                bm25_scores_norm = scaler.fit_transform(np.array(bm25_scores).reshape(-1, 1)).flatten()
            except Exception:
                bert_scores_norm = bert_sims
                bm25_scores_norm = bm25_scores

            alpha = 0.7
            final_scores = (alpha * bert_scores_norm) + ((1 - alpha) * bm25_scores_norm)

        for i, r in enumerate(candidates.itertuples(index=False)):
            results.append({
                "product_id": getattr(r, "product_id", None),
                "name": getattr(r, "name", None),
                "thumbnail_url": getattr(r, "thumbnail_url", None),
                "product_url": getattr(r, "product_url", None),
                "score": float(final_scores[i]),
            })
    else:
        # fallback: Word2Vec similarity (existing behavior)
        input_vec = _text_to_vector(full_text)
        for _, r in candidates.iterrows():
            text = (r.get("name", "") + " ") + (r.get("short_description", "") or r.get("description", ""))
            vec = _text_to_vector(text)
            score = _cosine(input_vec, vec)
            results.append({
                "product_id": r.get("product_id"),
                "name": r.get("name"),
                "thumbnail_url": r.get("thumbnail_url"),
                "product_url": r.get("product_url"),
                "score": score,
            })

    # sort and pick top_k
    results = sorted(results, key=lambda x: x["score"], reverse=True)
    top = results[:top_k]

    return {
        "input": {"title": title, "description": description, "base_category": base_category, "expanded_categories": categories},
        "suggestions": top,
    }
