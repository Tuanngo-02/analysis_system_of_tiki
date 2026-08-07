import re
import requests
import pickle
from pathlib import Path
import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.layers import Attention, Dense, Embedding

# Fix Attention cho Keras bản mới
class FixedAttention(Attention):
    @classmethod
    def from_config(cls, config):
        if not isinstance(config.get("score_mode"), str):
            config["score_mode"] = "dot"
        return cls(**config)


class CompatibleEmbedding(Embedding):
    """Load H5 models saved by Keras versions that emit quantization metadata."""

    @classmethod
    def from_config(cls, config):
        config = dict(config)
        config.pop("quantization_config", None)
        return cls(**config)


class CompatibleDense(Dense):
    @classmethod
    def from_config(cls, config):
        config = dict(config)
        config.pop("quantization_config", None)
        return cls(**config)

# Khởi tạo model và tokenizer (Singleton pattern để không load lại nhiều lần)
ASSET_DIR = Path(__file__).resolve().parents[1] / "model" / "model_sentiment"
MODEL_PATH = ASSET_DIR / "bilstm_sentiment.h5"
TOKENIZER_PATH = ASSET_DIR / "tokenizer.pkl"

_model = None
_tokenizer = None

def get_model():
    global _model
    if _model is None:
        _model = keras.models.load_model(
            MODEL_PATH,
            custom_objects={
                'Attention': FixedAttention,
                'Embedding': CompatibleEmbedding,
                'Dense': CompatibleDense,
            },
            compile=False
        )
    return _model

def get_tokenizer():
    global _tokenizer
    if _tokenizer is None:
        with open(TOKENIZER_PATH, 'rb') as f:
            _tokenizer = pickle.load(f)
    return _tokenizer

def extract_tiki_ids(url):
    pid_match = re.search(r'p(\d+)\.html', url)
    product_id = pid_match.group(1) if pid_match else None
    spid_match = re.search(r'spid=(\d+)', url)
    spid = spid_match.group(1) if spid_match else product_id
    return product_id, spid

def fetch_tiki_reviews(url):
    product_id, spid = extract_tiki_ids(url)

    if not product_id:
        return None

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json"
    }

    api_url = "https://tiki.vn/api/v2/reviews"

    all_reviews = []

    try:
        for page in range(1, 11):

            params = {
                "limit": 20,
                "page": page,
                "include": "comments,contribute_info,attribute_vote_summary",
                "sort": "score|desc,id|desc,stars|all",
                "spid": spid,
                "product_id": product_id
            }

            response = requests.get(
                api_url,
                headers=headers,
                params=params,
                timeout=10
            )

            if response.status_code != 200:
                break

            data = response.json()

            page_reviews = data.get("data", [])

            if not page_reviews:
                break

            for rv in page_reviews:

                content = rv.get("content")

                # chỉ lấy review có chữ
                if content and content.strip():
                    all_reviews.append(content.strip())

        # không có review text
        if len(all_reviews) == 0:
            return None

        return all_reviews

    except Exception as e:
        print("Fetch review error:", e)
        return None
def analyze_sentiment_logic(url: str):
    try:
        reviews = fetch_tiki_reviews(url)
        # bỏ qua sản phẩm không có review text
        if reviews is None:
            return None
        if not reviews:
            return {"status": "error", "message": "Không tìm thấy review nào hoặc URL sai."}

        model = get_model()
        tokenizer = get_tokenizer()
        
        sequences = tokenizer.texts_to_sequences(reviews)
        padded = pad_sequences(sequences, maxlen=100, padding='post', truncating='post')
        predictions = model.predict(padded, verbose=0)

        results = []
        for i, text in enumerate(reviews):
            score = float(predictions[i][0]) if predictions.shape[-1] == 1 else float(predictions[i][1])
            label = "Tích cực" if score > 0.5 else "Tiêu cực"
            results.append({
                "review": text,
                "label": label,
                "confidence": round(score, 2)
            })

        return {
            "product_url": url,
            "total_reviews": len(results),
            "data": results
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {
            "status": "error",
            "message": str(e)
        }
