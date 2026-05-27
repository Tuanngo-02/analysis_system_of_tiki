"""Lazy loading for FAISS, metadata, and embedding model."""

from __future__ import annotations

import pickle
from typing import Optional, Tuple

import faiss
import pandas as pd
from sentence_transformers import SentenceTransformer

from .constants import INDEX_PATH, METADATA_PATH, MODEL_NAME


_MODEL: Optional[SentenceTransformer] = None
_INDEX: Optional[faiss.Index] = None
_PRODUCTS: Optional[pd.DataFrame] = None


def load_resources() -> Tuple[Optional[SentenceTransformer], Optional[faiss.Index], pd.DataFrame]:
    """Load metadata first; use local SBERT/FAISS when available."""
    global _MODEL, _INDEX, _PRODUCTS
    if _PRODUCTS is None:
        with METADATA_PATH.open("rb") as file:
            _PRODUCTS = pickle.load(file).reset_index(drop=True)
    if _INDEX is None and INDEX_PATH.exists():
        _INDEX = faiss.read_index(str(INDEX_PATH))
    if _MODEL is None:
        try:
            _MODEL = SentenceTransformer(MODEL_NAME, device="cpu", local_files_only=True)
        except Exception:
            _MODEL = None
    return _MODEL, _INDEX, _PRODUCTS
