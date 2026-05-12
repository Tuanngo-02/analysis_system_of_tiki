import os

os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

import re
import requests
import pandas as pd
import pickle
import numpy as np
import tensorflow as tf
import keras
import streamlit as st

from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.layers import Attention


# ======================================================
# STREAMLIT CONFIG
# ======================================================
st.set_page_config(
    page_title="Tiki Sentiment Analysis",
    page_icon="🛍️",
    layout="wide"
)

st.title("🛍️ Phân tích cảm xúc Review Tiki")
st.write("Nhập link sản phẩm Tiki để phân tích cảm xúc review")


# ======================================================
# CUSTOM ATTENTION FIX
# ======================================================
class FixedAttention(Attention):

    @classmethod
    def from_config(cls, config):

        if not isinstance(config.get("score_mode"), str):
            config["score_mode"] = "dot"

        return cls(**config)


# ======================================================
# TÁCH PRODUCT ID
# ======================================================
def extract_tiki_ids(url):

    pid_match = re.search(r'p(\d+)\.html', url)
    product_id = pid_match.group(1) if pid_match else None

    spid_match = re.search(r'spid=(\d+)', url)
    spid = spid_match.group(1) if spid_match else product_id

    return product_id, spid


# ======================================================
# LẤY REVIEWS
# ======================================================
def get_raw_reviews(url):

    product_id, spid = extract_tiki_ids(url)

    if not product_id:
        return []

    headers = {
        'User-Agent': 'Mozilla/5.0',
        'Referer': url
    }

    api_url = "https://tiki.vn/api/v2/reviews"

    params = {
        'limit': 20,
        'include': 'comments',
        'sort': 'score|desc,id|desc,stars|all',
        'spid': spid,
        'product_id': product_id
    }

    try:

        response = requests.get(
            api_url,
            headers=headers,
            params=params,
            timeout=10
        )

        if response.status_code == 200:

            data = response.json()

            reviews = [
                rv.get('content', '')
                for rv in data.get('data', [])
                if rv.get('content')
            ]

            return reviews

    except Exception as e:

        st.error(f"Lỗi lấy review: {e}")

    return []


# ======================================================
# LOAD MODEL
# ======================================================
@st.cache_resource
def load_sentiment_model():

    model = keras.models.load_model(
        'bilstm_sentiment.h5',
        custom_objects={
            'Attention': FixedAttention
        },
        compile=False
    )

    return model


# ======================================================
# LOAD TOKENIZER
# ======================================================
@st.cache_resource
def load_tokenizer():

    with open('tokenizer.pkl', 'rb') as f:
        tokenizer = pickle.load(f)

    return tokenizer


# ======================================================
# PHÂN TÍCH
# ======================================================
def analyze_reviews(
    reviews,
    model,
    tokenizer,
    max_len=100
):

    sequences = tokenizer.texts_to_sequences(reviews)

    padded = pad_sequences(
        sequences,
        maxlen=max_len,
        padding='post',
        truncating='post'
    )

    predictions = model.predict(
        padded,
        verbose=0
    )

    results = []

    for i, text in enumerate(reviews):

        # sigmoid
        if predictions.shape[-1] == 1:

            score = float(predictions[i][0])

        # softmax
        else:

            score = float(predictions[i][1])

        label = (
            "😊 Tích cực"
            if score > 0.5
            else "😡 Tiêu cực"
        )

        results.append({
            "Review": text,
            "Kết quả": label,
            "Độ tin cậy": round(score, 2)
        })

    return pd.DataFrame(results)


# ======================================================
# GIAO DIỆN
# ======================================================
url_input = st.text_input(
    "🔗 Nhập link sản phẩm Tiki",
    placeholder="https://tiki.vn/..."
)

analyze_btn = st.button("🚀 Phân tích")


# ======================================================
# XỬ LÝ
# ======================================================
if analyze_btn:

    if not url_input:

        st.warning("⚠️ Vui lòng nhập link Tiki")

    else:

        with st.spinner("Đang tải model và phân tích..."):

            try:

                model = load_sentiment_model()
                tokenizer = load_tokenizer()

                reviews = get_raw_reviews(url_input)

                if not reviews:

                    st.error("❌ Không tìm thấy reviews")

                else:

                    st.success(f"✅ Lấy được {len(reviews)} reviews")

                    df = analyze_reviews(
                        reviews,
                        model,
                        tokenizer
                    )

                    st.subheader("📊 Kết quả phân tích")

                    st.dataframe(
                        df,
                        use_container_width=True
                    )

                    # =========================
                    # THỐNG KÊ
                    # =========================
                    positive_count = (
                        df["Kết quả"]
                        .str.contains("Tích cực")
                        .sum()
                    )

                    negative_count = (
                        df["Kết quả"]
                        .str.contains("Tiêu cực")
                        .sum()
                    )

                    total = len(df)

                    positive_ratio = positive_count / total

                    col1, col2, col3 = st.columns(3)

                    col1.metric(
                        "😊 Tích cực",
                        positive_count
                    )

                    col2.metric(
                        "😡 Tiêu cực",
                        negative_count
                    )

                    col3.metric(
                        "📈 Hài lòng",
                        f"{positive_ratio:.1%}"
                    )

                    # =========================
                    # KẾT LUẬN
                    # =========================
                    st.subheader("📝 Kết luận")

                    if positive_ratio >= 0.7:

                        st.success(
                            "Sản phẩm được đánh giá rất tốt."
                        )

                    elif positive_ratio >= 0.5:

                        st.info(
                            "Sản phẩm có đánh giá tương đối tích cực."
                        )

                    else:

                        st.error(
                            "Sản phẩm có nhiều đánh giá tiêu cực."
                        )

            except Exception as e:

                st.error(f"❌ Lỗi: {e}")