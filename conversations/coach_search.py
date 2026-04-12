"""
Semantic search over the local coaching knowledge base (A8-style retrieval).
Uses sentence-transformers (same family as rag-pipeline experiments) with
cosine similarity; no paid API.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import List, Tuple

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

KB_PATH = Path(__file__).resolve().parent / "data" / "coach_knowledge.md"
# Medium embedding model used in A8 RAG notebook experiments
EMBED_MODEL_NAME = "sentence-transformers/multi-qa-mpnet-base-cos-v1"
TOP_K = 5
MIN_SCORE = 0.28
MAX_QUERY_LEN = 500

_model = None
_chunk_texts: List[str] | None = None
_chunk_embeddings: np.ndarray | None = None


def _split_long_paragraph(text: str, max_words: int = 220) -> List[str]:
    words = text.split()
    if len(words) <= max_words:
        return [text]
    chunks: List[str] = []
    current: List[str] = []
    wc = 0
    for w in words:
        current.append(w)
        wc += 1
        if wc >= max_words:
            chunks.append(" ".join(current))
            current = []
            wc = 0
    if current:
        chunks.append(" ".join(current))
    return chunks


def _load_chunk_texts() -> List[str]:
    raw = KB_PATH.read_text(encoding="utf-8")
    paragraphs: List[str] = []
    for block in re.split(r"\n\s*\n", raw):
        block = block.strip()
        if not block:
            continue
        lines = []
        for line in block.split("\n"):
            line = line.strip()
            if line.startswith("#"):
                continue
            lines.append(line)
        merged = " ".join(lines).strip()
        if not merged:
            continue
        for piece in _split_long_paragraph(merged):
            if piece:
                paragraphs.append(piece)
    if not paragraphs:
        raise RuntimeError("Coach knowledge base is empty or unreadable.")
    return paragraphs


def _get_model():
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer

        _model = SentenceTransformer(EMBED_MODEL_NAME)
    return _model


def _ensure_index() -> None:
    global _chunk_texts, _chunk_embeddings
    if _chunk_embeddings is not None and _chunk_texts is not None:
        return
    _chunk_texts = _load_chunk_texts()
    model = _get_model()
    emb = model.encode(
        _chunk_texts,
        normalize_embeddings=True,
        show_progress_bar=False,
        convert_to_numpy=True,
    )
    _chunk_embeddings = np.asarray(emb, dtype=np.float32)


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

    _ensure_index()
    assert _chunk_texts is not None and _chunk_embeddings is not None

    model = _get_model()
    q_emb = model.encode(
        [q],
        normalize_embeddings=True,
        show_progress_bar=False,
        convert_to_numpy=True,
    )
    sims = cosine_similarity(q_emb, _chunk_embeddings)[0]
    order = np.argsort(-sims)[:TOP_K]
    results: List[dict] = []
    for i in order:
        score = float(sims[int(i)])
        if score < MIN_SCORE:
            continue
        results.append({"text": _chunk_texts[int(i)], "score": round(score, 4)})
    if not results:
        return [], (
            "No passages matched strongly enough for that query. "
            "Try different keywords (for example: filler words, pacing, confidence, feedback)."
        )
    return results, None
