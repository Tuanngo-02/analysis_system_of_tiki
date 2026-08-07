"""BiLSTM category prediction service.

Nhận link Tiki -> crawl tên sản phẩm -> preprocess -> dự đoán danh mục.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, Optional, Tuple

import joblib
import numpy as np
import requests

try:
    from bs4 import BeautifulSoup
except Exception:
    BeautifulSoup = None

try:
    from tensorflow.keras.models import load_model
    from tensorflow.keras.layers import Dense, Embedding
    from tensorflow.keras.preprocessing.sequence import pad_sequences
    _TF_OK = True
except Exception:
    load_model = None
    Embedding = None
    Dense = None
    pad_sequences = None
    _TF_OK = False


MODEL_FILENAME = "bilstm_category_model.h5"
TOKENIZER_FILENAME = "tokenizer.pkl"
LABEL_ENCODER_FILENAME = "label_encoder.pkl"
MAX_LEN = 100


class _Cache:
    model = None
    tokenizer = None
    label_encoder = None


_cache = _Cache()


if Embedding is not None:
    class CompatibleEmbedding(Embedding):
        """Ignore Keras quantization metadata unsupported by legacy H5 loading."""

        @classmethod
        def from_config(cls, config):
            config = dict(config)
            config.pop("quantization_config", None)
            return cls(**config)
else:
    CompatibleEmbedding = None


if Dense is not None:
    class CompatibleDense(Dense):
        @classmethod
        def from_config(cls, config):
            config = dict(config)
            config.pop("quantization_config", None)
            return cls(**config)
else:
    CompatibleDense = None


def _find_modelcategory_file(filename: str) -> Path:
    here = Path(__file__).resolve()
    for parent in list(here.parents)[:6] + [Path.cwd()]:
        candidate = parent / "modelcategory" / filename
        if candidate.exists():
            return candidate
    raise FileNotFoundError(f"Không tìm thấy file modelcategory/{filename}")


def _clean_text(text: str) -> str:
    text = str(text or "").lower().strip()
    text = re.sub(r"[\t\n\r]+", " ", text)
    text = re.sub(r"[^\w\sÀ-ỹđĐ]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def _load_assets() -> None:
    if _cache.model is not None and _cache.tokenizer is not None:
        return
    if not _TF_OK:
        return

    try:
        model_path = _find_modelcategory_file(MODEL_FILENAME)
        tokenizer_path = _find_modelcategory_file(TOKENIZER_FILENAME)
        label_encoder_path = _find_modelcategory_file(LABEL_ENCODER_FILENAME)

        _cache.model = load_model(
            str(model_path),
            custom_objects={
                "Embedding": CompatibleEmbedding,
                "Dense": CompatibleDense,
            },
            compile=False,
        )
        _cache.tokenizer = joblib.load(str(tokenizer_path))
        _cache.label_encoder = joblib.load(str(label_encoder_path))
    except Exception:
        _cache.model = None
        _cache.tokenizer = None
        _cache.label_encoder = None


def _crawl_tiki_title(product_url: str) -> str:
    if BeautifulSoup is None:
        return ""

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
        ),
        "Accept-Language": "vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7",
        "Referer": "https://tiki.vn/",
    }

    resp = requests.get(product_url, headers=headers, timeout=15)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    title_tag = soup.find("meta", property="og:title")
    if title_tag and title_tag.get("content"):
        return title_tag.get("content", "").strip()

    h1 = soup.find("h1")
    if h1:
        return h1.get_text(strip=True)

    return ""


def predict_category(product_name: str) -> Tuple[str, float]:
    """Predict category from product name using BiLSTM.

    Returns:
        (category, confidence_percent)
    """
    _load_assets()

    if _cache.model is None or _cache.tokenizer is None or pad_sequences is None:
        raise RuntimeError("BiLSTM model/tokenizer is not available")

    normalized_name = _clean_text(product_name)
    seq = _cache.tokenizer.texts_to_sequences([normalized_name])
    padded = pad_sequences(seq, maxlen=MAX_LEN, padding="post", truncating="post")

    pred = _cache.model.predict(padded, verbose=0)
    class_idx = int(np.argmax(pred, axis=1)[0])
    confidence = float(np.max(pred)) * 100.0

    category = None
    if _cache.label_encoder is not None and hasattr(_cache.label_encoder, "inverse_transform"):
        try:
            category = _cache.label_encoder.inverse_transform([class_idx])[0]
        except Exception:
            category = None

    if category is None:
        classes = getattr(_cache.label_encoder, "classes_", None)
        if classes is not None and 0 <= class_idx < len(classes):
            category = classes[class_idx]
        else:
            category = str(class_idx)

    return str(category), confidence


def predict_category_from_url(product_url: str) -> Dict:
    title = _crawl_tiki_title(product_url)
    if not title:
        raise ValueError("Không crawl được tên sản phẩm từ link Tiki")

    category, confidence = predict_category(title)
    return {
        "input": {
            "product_url": product_url,
            "title": title,
        },
        "prediction": {
            "category": category,
            "confidence": round(confidence, 2),
            "model": "bilstm",
        },
    }
