"""
Hosted summarization via Hugging Face Inference Providers (chat completion).
Uses HF_TOKEN from the environment, same pattern as conversations.views.api_action_items.
"""
from __future__ import annotations

import os
import re

from huggingface_hub import InferenceClient

MAX_INPUT_CHARS = 4000
MAX_TOKENS = 160
MIN_WORDS_TO_SUMMARIZE = 12
DEFAULT_MODEL = "Qwen/Qwen2.5-7B-Instruct"

_ECHO_PREFIXES = (
    "summarize what this person said in 1-2 sentences",
    "summarize what the person said",
    "here is the summary",
    "summary:",
)

_client: InferenceClient | None = None


def _get_client() -> InferenceClient:
    global _client
    if _client is None:
        token = os.environ.get("HF_TOKEN") or os.environ.get("HUGGINGFACE_TOKEN")
        if not token:
            raise RuntimeError(
                "HF_TOKEN is not set. Add it to .env (dev) or to your host's "
                "environment variables (prod) to enable summarization."
            )
        _client = InferenceClient(token=token)
    return _client


def _preprocess(text: str) -> str:
    if not text or not isinstance(text, str):
        return ""
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) > MAX_INPUT_CHARS:
        text = text[:MAX_INPUT_CHARS] + "..."
    return text


def _word_count(text: str) -> int:
    return len(text.split())


def _strip_echoed_instruction(summary: str) -> str:
    s = summary.strip()
    lower = s.lower()
    for prefix in _ECHO_PREFIXES:
        if lower.startswith(prefix):
            s = s[len(prefix):].lstrip(" :")
            lower = s.lower()
    return s.strip()


def summarize_transcript(text: str) -> str:
    """
    Summarize a transcript via Hugging Face Inference. Returns a short string.
    """
    text = _preprocess(text)
    if not text:
        return "No transcript text to summarize."
    if _word_count(text) < MIN_WORDS_TO_SUMMARIZE:
        return (
            "This transcript is too short to summarize reliably. "
            "Add more transcript segments or real spoken content, then try again."
        )

    model_id = os.environ.get("HF_SUMMARY_MODEL", DEFAULT_MODEL)
    prompt = (
        "Summarize the following conversation transcript in 1-2 sentences. "
        "Use only information from the transcript. Do not add commentary, "
        "speaker labels, or instructions in your reply.\n\n"
        f"{text}"
    )
    client = _get_client()
    response = client.chat_completion(
        model=model_id,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=MAX_TOKENS,
        temperature=0.2,
    )
    summary = ""
    try:
        summary = response.choices[0].message.content or ""
    except (AttributeError, IndexError, TypeError):
        summary = ""
    summary = _strip_echoed_instruction(summary)
    if not summary:
        return "Could not generate summary."
    return summary.strip()
