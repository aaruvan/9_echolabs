"""
Build the coach knowledge embedding index offline.

Run once locally (in a venv that still has sentence-transformers) before deploying.
Output: conversations/data/coach_index.json — committed and shipped to prod.

Runtime (conversations/coach_search.py) loads this JSON and queries embeddings
via the Hugging Face Inference API, so production has no torch/sklearn deps.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import numpy as np
import torch
from transformers import AutoTokenizer, AutoModel

REPO_ROOT = Path(__file__).resolve().parent.parent
KB_PATH = REPO_ROOT / "conversations" / "data" / "coach_knowledge.md"
OUT_PATH = REPO_ROOT / "conversations" / "data" / "coach_index.json"
EMBED_MODEL_NAME = "sentence-transformers/multi-qa-mpnet-base-cos-v1"


def _mean_pool(last_hidden_state: torch.Tensor, attention_mask: torch.Tensor) -> torch.Tensor:
    mask = attention_mask.unsqueeze(-1).expand(last_hidden_state.size()).float()
    summed = torch.sum(last_hidden_state * mask, dim=1)
    counts = torch.clamp(mask.sum(dim=1), min=1e-9)
    return summed / counts


def _embed(texts: list[str], tokenizer, model) -> np.ndarray:
    out: list[np.ndarray] = []
    for i in range(0, len(texts), 16):
        batch = texts[i : i + 16]
        enc = tokenizer(batch, padding=True, truncation=True, return_tensors="pt", max_length=512)
        with torch.no_grad():
            model_out = model(**enc)
        pooled = _mean_pool(model_out.last_hidden_state, enc["attention_mask"])
        pooled = torch.nn.functional.normalize(pooled, p=2, dim=1)
        out.append(pooled.cpu().numpy().astype(np.float32))
    return np.concatenate(out, axis=0)


def _split_long_paragraph(text: str, max_words: int = 220) -> list[str]:
    words = text.split()
    if len(words) <= max_words:
        return [text]
    chunks: list[str] = []
    current: list[str] = []
    for w in words:
        current.append(w)
        if len(current) >= max_words:
            chunks.append(" ".join(current))
            current = []
    if current:
        chunks.append(" ".join(current))
    return chunks


def load_chunks() -> list[str]:
    raw = KB_PATH.read_text(encoding="utf-8")
    paragraphs: list[str] = []
    for block in re.split(r"\n\s*\n", raw):
        block = block.strip()
        if not block:
            continue
        lines = [ln.strip() for ln in block.split("\n") if ln.strip() and not ln.strip().startswith("#")]
        merged = " ".join(lines).strip()
        if not merged:
            continue
        paragraphs.extend(p for p in _split_long_paragraph(merged) if p)
    if not paragraphs:
        raise RuntimeError("Coach knowledge base is empty or unreadable.")
    return paragraphs


def main() -> None:
    chunks = load_chunks()
    tokenizer = AutoTokenizer.from_pretrained(EMBED_MODEL_NAME)
    model = AutoModel.from_pretrained(EMBED_MODEL_NAME)
    model.eval()
    embeddings = _embed(chunks, tokenizer, model)
    payload = {
        "model": EMBED_MODEL_NAME,
        "dim": int(embeddings.shape[1]),
        "chunks": chunks,
        "embeddings": embeddings.tolist(),
    }
    OUT_PATH.write_text(json.dumps(payload), encoding="utf-8")
    print(f"Wrote {len(chunks)} chunks ({embeddings.shape}) to {OUT_PATH}")


if __name__ == "__main__":
    main()
