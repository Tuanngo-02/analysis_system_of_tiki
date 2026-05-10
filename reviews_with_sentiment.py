import pandas as pd
import pickle
import re

from underthesea import word_tokenize
from tensorflow.keras.preprocessing.sequence import pad_sequences
import keras

# =========================
# Load model
# =========================
print("Loading model...")

model = keras.models.load_model(
    "bilstm_sentiment.h5",
    compile=False
)

print("Model loaded")

# =========================
# Load tokenizer
# =========================
print("Loading tokenizer...")

with open("tokenizer.pkl", "rb") as f:
    tokenizer = pickle.load(f)

print("Tokenizer loaded")

# =========================
# Load dataset
# =========================
print("Loading dataset...")

df = pd.read_csv("tiki_reviews_category.csv")

print(f"Dataset loaded: {len(df)} reviews")

# =========================
# Clean text
# =========================
def clean_text(text):

    text = str(text).lower()

    text = re.sub(r'http\S+|www\S+', ' ', text)

    text = re.sub(r'\d+', ' ', text)

    text = re.sub(r'[^\w\s]', ' ', text)

    text = re.sub(r'\s+', ' ', text).strip()

    return text

# =========================
# Preprocess
# =========================
def preprocess_text(text):

    text = clean_text(text)

    text = word_tokenize(text, format="text")

    return text

# =========================
# Preprocess all reviews
# =========================
print("Preprocessing reviews...")

texts = []

for i, review in enumerate(df['review_text']):

    text = preprocess_text(review)

    texts.append(text)

    if (i + 1) % 1000 == 0:
        print(f"Processed {i + 1} reviews")

print("Preprocessing done")

# =========================
# Convert to sequences
# =========================
print("Converting to sequences...")

seqs = tokenizer.texts_to_sequences(texts)

pads = pad_sequences(
    seqs,
    maxlen=100,
    padding='post',
    truncating='post'
)

print("Padding done")

# =========================
# Predict batch
# =========================
print("Predicting sentiments...")

preds = model.predict(
    pads,
    batch_size=256,
    verbose=1
)

print("Prediction done")

# =========================
# Convert probability -> label
# =========================
predictions = (preds > 0.5).astype(int).flatten()

# thêm cột sentiment
df['predicted_sentiment'] = predictions

# =========================
# Save result
# =========================
output_file = "reviews_with_sentiment.csv"

df.to_csv(
    output_file,
    index=False
)

print(f"Saved to {output_file}")
print("DONE")