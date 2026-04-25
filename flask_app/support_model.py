"""
support_model.py — Adapted from inesgcalvo/neuro_papers_db/src/support_model.py
Handles text preprocessing, embedding generation, and journal prediction.
"""

import re
import os
import numpy as np
import pandas as pd

import nltk
# Download NLTK data if not already present
for resource in ("punkt", "stopwords", "punkt_tab"):
    try:
        nltk.data.find(f"tokenizers/{resource}" if "punkt" in resource else f"corpora/{resource}")
    except LookupError:
        nltk.download(resource, quiet=True)

from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

from sklearn.decomposition import PCA

import tensorflow as tf
from keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences


# ── Text preprocessing ────────────────────────────────────────────────────

def preprocess_text(text: str) -> str:
    """
    Lowercase, strip non-alpha characters, tokenize, remove English stopwords.
    """
    text = text.lower()
    text = re.sub(r"[^a-z\s]", "", text)
    tokens = word_tokenize(text)
    stop_words = set(stopwords.words("english"))
    tokens = [t for t in tokens if t not in stop_words]
    return " ".join(tokens)


def preprocess_input(title: str, abstract: str):
    return preprocess_text(title), preprocess_text(abstract)


# ── Embedding generation ──────────────────────────────────────────────────

def column_embeddings(df: pd.DataFrame, col: str, n_components: int = 1) -> pd.DataFrame:
    """
    Tokenize → Keras Embedding layer → PCA dimensionality reduction.
    Matches the training pipeline used in neuro_papers_db.
    """
    df = df.copy()
    df[col] = df[col].astype(str)

    tokenizer = Tokenizer()
    tokenizer.fit_on_texts(df[col])
    total_words = len(tokenizer.word_index) + 1
    sequences = tokenizer.texts_to_sequences(df[col])
    padded = pad_sequences(sequences)

    embedding_dim = 100
    model = tf.keras.models.Sequential([
        tf.keras.layers.Embedding(
            input_dim=total_words,
            output_dim=embedding_dim,
            input_length=padded.shape[1],
        )
    ])

    embeddings = model.predict(padded, verbose=0)
    embeddings_flat = np.array([emb.flatten() for emb in embeddings])

    pca = PCA(n_components=n_components)
    embeddings_reduced = pca.fit_transform(embeddings_flat)
    cols = [f"{col}_emb_{i}" for i in range(n_components)]
    return pd.DataFrame(embeddings_reduced, columns=cols)


def generate_input_embeddings(title: str, abstract: str) -> pd.Series:
    title_emb    = column_embeddings(pd.DataFrame({"input": [title]}),    "input", 1).iloc[0]
    abstract_emb = column_embeddings(pd.DataFrame({"input": [abstract]}), "input", 1).iloc[0]
    return pd.concat([title_emb, abstract_emb], axis=0)


# ── Prediction pipeline ───────────────────────────────────────────────────

def predict_journal(model, input_embeddings: pd.Series):
    reshaped   = input_embeddings.values.reshape(1, -1)
    prediction = model.predict(reshaped)
    probability = model.predict_proba(reshaped)
    return prediction, probability


def get_results(prediction, probability, label_encoder) -> list:
    decoded = label_encoder.inverse_transform(prediction)
    return [
        {"journal": journal, "probability": float(prob)}
        for journal, prob in zip(decoded, probability[0])
    ]


def predict_journal_for_input(title: str, abstract: str, model, label_encoder) -> list:
    """
    Full pipeline: raw title + abstract → sorted list of {journal, probability}.
    """
    title, abstract = preprocess_input(title, abstract)
    embeddings = generate_input_embeddings(title, abstract)
    prediction, probability = predict_journal(model, embeddings)
    return get_results(prediction, probability, label_encoder)
