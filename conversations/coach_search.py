"""
Semantic search over the coaching knowledge base.

Embeddings for the corpus are pre-computed offline by scripts/build_coach_index.py
and shipped as conversations/data/coach_index.json. At runtime, only the query
embedding is computed on demand via the Hugging Face Inference API, so production
needs no torch / sentence-transformers / sklearn dependencies.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import List, Tuple

import numpy as np
from huggingface_hub import InferenceClient

INDEX_PATH = Path(__file__).resolve().parent / "data" / "coach_index.json"
TOP_K = 5
MIN_SCORE = 0.28
MAX_QUERY_LEN = 500

_chunks: List[str] | None = None
_embeddings: np.ndarray | None = None
_index_model: str | None = None
_client: InferenceClient | None = None


def _load_index() -> None:
    global _chunks, _embeddings, _index_model
    if _embeddings is not None:
        return
    if not INDEX_PATH.is_file():
        raise RuntimeError(
            f"Coach index not found at {INDEX_PATH}. "
            "Run `python scripts/build_coach_index.py` to generate it."
        )
    payload = json.loads(INDEX_PATH.read_text(encoding="utf-8"))
    _chunks = list(payload["chunks"])
    _embeddings = np.asarray(payload["embeddings"], dtype=np.float32)
    _index_model = str(payload["model"])


def _get_client() -> InferenceClient:
    global _client
    if _client is None:
        token = os.environ.get("HF_TOKEN") or os.environ.get("HUGGINGFACE_TOKEN")
        if not token:
            raise RuntimeError(
                "HF_TOKEN is not set. Add it to .env (dev) or to your host's "
                "environment variables (prod) to enable coach search."
            )
        _client = InferenceClient(token=token)
    return _client


def _embed_query(text: str) -> np.ndarray:
    """Return a 1-D, L2-normalized query embedding matching the index dim."""
    assert _index_model is not None
    client = _get_client()
    raw = client.feature_extraction(text, model=_index_model)
    arr = np.asarray(raw, dtype=np.float32)
    # The Inference API may return (dim,) (already pooled) or (seq_len, dim)
    # (token-level). Mean-pool token-level outputs to match the index.
    if arr.ndim == 2:
        arr = arr.mean(axis=0)
    elif arr.ndim == 3:
        arr = arr.mean(axis=1).squeeze(0)
    norm = np.linalg.norm(arr)
    if norm > 0:
        arr = arr / norm
    return arr


def _cosine(query: np.ndarray, matrix: np.ndarray) -> np.ndarray:
    # Index embeddings are already L2-normalized; query is normalized in _embed_query.
    return matrix @ query


def search(query: str) -> Tuple[List[dict], str | None]:
    """
    Return (results, no_match_message).
    Each result is {"text": str, "score": float}.
    no_match_message is set when nothing clears MIN_SCORE.
    """
    q = (query or "").strip()
    if not q:
        raise ValueError("Query cannot be empty.")
    if len(q) > MAX_QUERY_LEN:
        raise ValueError(f"Query must be at most {MAX_QUERY_LEN} characters.")

    _load_index()
    assert _chunks is not None and _embeddings is not None

    q_emb = _embed_query(q)
    if q_emb.shape[0] != _embeddings.shape[1]:
        raise RuntimeError(
            f"Query embedding dim ({q_emb.shape[0]}) does not match index dim "
            f"({_embeddings.shape[1]}). Rebuild the index with the same model."
        )

    sims = _cosine(q_emb, _embeddings)
    order = np.argsort(-sims)[:TOP_K]
    results: List[dict] = []
    for i in order:
        score = float(sims[int(i)])
        if score < MIN_SCORE:
            continue
        results.append({"text": _chunks[int(i)], "score": round(score, 4)})
    if not results:
        return [], (
            "No passages matched strongly enough for that query. "
            "Try different keywords (for example: filler words, pacing, confidence, feedback)."
        )
    return results, None
