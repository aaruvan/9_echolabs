"""
Local LLM summarization using Hugging Face transformers.
Uses philschmid/bart-large-cnn-samsum (chosen in ai_prototype.ipynb).
Model weights are loaded on first use and cached.

The model was benchmarked in ai_prototype.ipynb with raw transcript (zero-shot), not an
instruction prefix; adding "Summarize..." can make the model echo the instruction or
regurgitate input on short or placeholder text.
"""
import re

# Lazy-loaded model and tokenizer (loaded on first summarize_transcript call)
_tokenizer = None
_model = None
MODEL_NAME = "philschmid/bart-large-cnn-samsum"
MAX_INPUT_LENGTH = 512
MAX_NEW_TOKENS = 80
# Avoid summarizing seed placeholders or a single short line (model will hallucinate).
MIN_WORDS_TO_SUMMARIZE = 12
_ECHO_PREFIXES = (
    "summarize what this person said in 1-2 sentences",
    "summarize what the person said",
)


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


def _word_count(text: str) -> int:
    return len(text.split())


def _strip_echoed_instruction(summary: str) -> str:
    """Remove leading instruction echo if the model regurgitates the prompt style."""
    s = summary.strip()
    lower = s.lower()
    for prefix in _ECHO_PREFIXES:
        if lower.startswith(prefix):
            rest = s[len(prefix) :].lstrip(" :")
            s = rest
            lower = s.lower()
    return s.strip()


def summarize_transcript(text: str) -> str:
    """
    Summarize transcript text using the local BART model.
    Returns summary string or raises on error.
    """
    text = _preprocess(text)
    if not text:
        return "No transcript text to summarize."
    if _word_count(text) < MIN_WORDS_TO_SUMMARIZE:
        return (
            "This transcript is too short to summarize reliably. "
            "Add more transcript segments or real spoken content, then try again."
        )
    tokenizer, model = _get_model()
    import torch
    inputs = tokenizer(
        text,
        return_tensors="pt",
        max_length=MAX_INPUT_LENGTH,
        truncation=True,
    )
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=MAX_NEW_TOKENS,
            num_beams=4,
            no_repeat_ngram_size=3,
        )
    summary = tokenizer.decode(outputs[0], skip_special_tokens=True)
    summary = _strip_echoed_instruction(summary)
    if not summary:
        return "Could not generate summary."
    return summary.strip()
