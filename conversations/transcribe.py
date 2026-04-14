"""
Local speech-to-text with WhisperX: ASR + alignment + pyannote speaker diarization.
Requires HF_TOKEN (read) in the environment and accepting pyannote model terms on Hugging Face.
"""
from __future__ import annotations

import gc
import os
import re
import shutil
import subprocess
from pathlib import Path

# Sync upload policy: keep CPU/GPU time and HTTP request bounded for local dev.
MAX_AUDIO_DURATION_SEC = int(os.environ.get("WHISPER_MAX_DURATION_SEC", "300"))  # 5 min
MAX_FILE_BYTES = int(os.environ.get("WHISPER_MAX_FILE_BYTES", str(25 * 1024 * 1024)))

_asr_model = None
_asr_cache_key: tuple[str, str, str] | None = None
_diarize_pipeline = None
_diarize_cache_key: tuple[str, str] | None = None


def _probe_duration_seconds(path: str) -> float | None:
    """Best-effort duration via ffprobe; returns None if unavailable."""
    try:
        r = subprocess.run(
            [
                "ffprobe",
                "-v",
                "error",
                "-show_entries",
                "format=duration",
                "-of",
                "default=noprint_wrappers=1:nokey=1",
                path,
            ],
            capture_output=True,
            text=True,
            timeout=60,
            check=False,
        )
        if r.returncode != 0 or not (r.stdout or "").strip():
            return None
        return float((r.stdout or "").strip())
    except (FileNotFoundError, ValueError, subprocess.TimeoutExpired):
        return None


def _pick_device() -> str:
    if os.environ.get("WHISPER_FORCE_CPU", "").lower() in ("1", "true", "yes"):
        return "cpu"
    try:
        import torch

        if torch.cuda.is_available():
            return "cuda"
    except ImportError:
        pass
    return "cpu"


def _get_hf_token() -> str:
    token = (os.environ.get("HF_TOKEN") or os.environ.get("HUGGINGFACE_TOKEN") or "").strip()
    if not token:
        raise ValueError(
            "HF_TOKEN (or HUGGINGFACE_TOKEN) is required for speaker diarization. "
            "Create a read token at https://huggingface.co/settings/tokens, add it to .env, "
            "and accept the user agreement for the pyannote diarization model used by WhisperX "
            "(see README)."
        )
    return token


def _get_asr_model():
    """Cache WhisperX ASR model per (name, device, compute_type, preset language)."""
    global _asr_model, _asr_cache_key
    import whisperx

    device = _pick_device()
    compute_type = os.environ.get("WHISPER_COMPUTE_TYPE") or (
        "float16" if device == "cuda" else "float32"
    )
    name = os.environ.get("WHISPER_MODEL", "base")
    preset_lang = (os.environ.get("WHISPER_LANGUAGE") or "").strip() or None
    hf_token = _get_hf_token()
    key = (name, device, compute_type, preset_lang or "")
    if _asr_model is None or _asr_cache_key != key:
        _asr_model = whisperx.load_model(
            name,
            device,
            compute_type=compute_type,
            language=preset_lang,
            use_auth_token=hf_token,
        )
        _asr_cache_key = key
    return _asr_model, device


def _get_diarize_pipeline(hf_token: str, device: str):
    global _diarize_pipeline, _diarize_cache_key
    from whisperx.diarize import DiarizationPipeline

    key = (device, hf_token)
    if _diarize_pipeline is None or _diarize_cache_key != key:
        model_name = os.environ.get("WHISPERX_DIARIZE_MODEL")
        kwargs = {"token": hf_token, "device": device}
        if model_name:
            kwargs["model_name"] = model_name
        _diarize_pipeline = DiarizationPipeline(**kwargs)
        _diarize_cache_key = key
    return _diarize_pipeline


def _format_speaker_label(raw: str | None) -> str:
    """Map pyannote-style ids to Speaker A, Speaker B, …"""
    if raw is None or str(raw).strip() == "":
        return ""
    s = str(raw).strip()
    m = re.match(r"SPEAKER_(\d+)$", s, re.IGNORECASE)
    if m:
        n = int(m.group(1))
        if 0 <= n < 26:
            return f"Speaker {chr(ord('A') + n)}"
        return f"Speaker {n + 1}"
    return s[:64]


def _env_int(name: str) -> int | None:
    v = (os.environ.get(name) or "").strip()
    return int(v) if v.isdigit() else None


def _require_ffmpeg() -> None:
    """WhisperX decodes most formats via a subprocess to `ffmpeg`."""
    if shutil.which("ffmpeg") is None:
        raise ValueError(
            "FFmpeg is not installed or not on your PATH. WhisperX needs the `ffmpeg` "
            "command to decode audio. Install FFmpeg (macOS: `brew install ffmpeg`), "
            "open a new terminal so PATH updates, then restart `runserver`."
        )


def transcribe_audio_file(path: str) -> tuple[list[tuple[str, str]], float]:
    """
    Transcribe audio at path with WhisperX + diarization.

    Returns (list of (speaker_label, segment_text), duration_seconds).
    speaker_label may be empty if diarization could not assign a speaker.
    """
    import torch
    import whisperx

    p = Path(path)
    if not p.is_file():
        raise ValueError("Audio file is missing or invalid.")

    size = p.stat().st_size
    if size > MAX_FILE_BYTES:
        raise ValueError(
            f"File is too large ({size // (1024 * 1024)} MB). "
            f"Maximum size is {MAX_FILE_BYTES // (1024 * 1024)} MB."
        )

    probed = _probe_duration_seconds(str(p))
    if probed is not None and probed > MAX_AUDIO_DURATION_SEC:
        raise ValueError(
            f"Audio is too long ({int(probed)}s). "
            f"Maximum is {MAX_AUDIO_DURATION_SEC} seconds (~{MAX_AUDIO_DURATION_SEC // 60} minutes)."
        )

    hf_token = _get_hf_token()
    _require_ffmpeg()
    audio = whisperx.load_audio(str(p))
    model, device = _get_asr_model()
    batch_size = _env_int("WHISPERX_BATCH_SIZE") or (8 if device == "cuda" else 4)

    result = model.transcribe(
        audio,
        batch_size=batch_size,
        language=os.environ.get("WHISPER_LANGUAGE") or None,
    )
    if not result.get("segments"):
        raise ValueError(
            "No speech detected in the audio. Try a clearer recording or a different format."
        )

    language = result.get("language") or "en"
    align_model, align_metadata = whisperx.load_align_model(
        language_code=language,
        device=device,
    )
    try:
        aligned = whisperx.align(
            result["segments"],
            align_model,
            align_metadata,
            audio,
            device,
            return_char_alignments=False,
        )
        result["segments"] = aligned["segments"]
    finally:
        del align_model
        gc.collect()
        if device == "cuda":
            torch.cuda.empty_cache()

    min_speakers = _env_int("WHISPERX_MIN_SPEAKERS")
    max_speakers = _env_int("WHISPERX_MAX_SPEAKERS")
    diarize_kw: dict = {}
    if min_speakers is not None:
        diarize_kw["min_speakers"] = min_speakers
    if max_speakers is not None:
        diarize_kw["max_speakers"] = max_speakers

    diarize_model = _get_diarize_pipeline(hf_token, device)
    diarize_segments = diarize_model(audio, **diarize_kw)
    result = whisperx.assign_word_speakers(
        diarize_segments, result, fill_nearest=True
    )

    rows: list[tuple[str, str]] = []
    ends: list[float] = []
    for seg in result.get("segments") or []:
        text = (seg.get("text") or "").strip()
        if not text:
            continue
        raw = seg.get("speaker")
        label = _format_speaker_label(raw) if raw is not None else ""
        rows.append((label, text))
        end = seg.get("end")
        if isinstance(end, (int, float)):
            ends.append(float(end))

    duration = max(ends) if ends else 0.0
    if duration > MAX_AUDIO_DURATION_SEC:
        raise ValueError(
            f"Audio is too long ({int(duration)}s). "
            f"Maximum is {MAX_AUDIO_DURATION_SEC} seconds."
        )

    if not rows:
        raise ValueError(
            "No speech detected in the audio. Try a clearer recording or a different format."
        )

    return rows, duration
