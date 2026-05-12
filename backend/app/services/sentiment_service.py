import os
import re
import requests
import pickle
import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.layers import Attention

# Fix Attention cho Keras bản mới
class FixedAttention(Attention):
    @classmethod
    def from_config(cls, config):
        if not isinstance(config.get("score_mode"), str):
            config["score_mode"] = "dot"
        return cls(**config)

# Khởi tạo model và tokenizer (Singleton pattern để không load lại nhiều lần)
MODEL_PATH = 'app/model/model_sentiment/bilstm_sentiment.h5'
TOKENIZER_PATH = 'app/model/model_sentiment/tokenizer.pkl'

_model = None
_tokenizer = None

def get_model():
    global _model
    if _model is None:
        _model = keras.models.load_model(
            MODEL_PATH,
            custom_objects={'Attention': FixedAttention},
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
    if not product_id: return []
    
    headers = {'User-Agent': 'Mozilla/5.0'}
    api_url = "https://tiki.vn/api/v2/reviews"
    params = {
        'limit': 10, # Giới hạn để API chạy nhanh
        'spid': spid,
        'product_id': product_id
    }
    
    try:
        response = requests.get(api_url, headers=headers, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return [rv.get('content', '') for rv in data.get('data', []) if rv.get('content')]
    except Exception:
        return []
    return []

def analyze_sentiment_logic(url: str):
    reviews = fetch_tiki_reviews(url)
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