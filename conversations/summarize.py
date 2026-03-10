"""
Local LLM summarization using Hugging Face transformers.
Uses philschmid/bart-large-cnn-samsum (chosen in ai_prototype.ipynb).
Model weights are loaded on first use and cached.
"""
import re

# Lazy-loaded model and tokenizer (loaded on first summarize_transcript call)
_tokenizer = None
_model = None
MODEL_NAME = "philschmid/bart-large-cnn-samsum"
PROMPT_PREFIX = "Summarize what this person said in 1-2 sentences: "
MAX_INPUT_LENGTH = 512
MAX_NEW_TOKENS = 60


def _get_model():
    """Load and cache tokenizer and model (lazy load)."""
    global _tokenizer, _model
    if _model is None:
        from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
        import torch
        _tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
        _model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME)
        _model.eval()
    return _tokenizer, _model


def _preprocess(text: str) -> str:
    """Clean and truncate transcript for the model."""
    if not text or not isinstance(text, str):
        return ""
    # Normalize whitespace
    text = re.sub(r"\s+", " ", text).strip()
    # Truncate by character count (roughly under 512 tokens for most inputs)
    if len(text) > 2000:
        text = text[:2000] + "..."
    return text


def summarize_transcript(text: str) -> str:
    """
    Summarize transcript text using the local BART model.
    Returns summary string or raises on error.
    """
    text = _preprocess(text)
    if not text:
        return "No transcript text to summarize."
    tokenizer, model = _get_model()
    import torch
    full_input = PROMPT_PREFIX + text
    inputs = tokenizer(
        full_input,
        return_tensors="pt",
        max_length=MAX_INPUT_LENGTH,
        truncation=True,
    )
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=MAX_NEW_TOKENS,
            num_beams=4,
        )
    summary = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return summary.strip() if summary else "Could not generate summary."
