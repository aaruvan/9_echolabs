"""
Hosted speech-to-text via AssemblyAI: transcription + speaker diarization in one call.
Requires ASSEMBLYAI_API_KEY in the environment.
"""
from __future__ import annotations

import os
import re
import shutil
import subprocess
import time
from pathlib import Path

import requests

# Sync upload policy: bound HTTP request time and prevent runaway costs.
MAX_AUDIO_DURATION_SEC = int(os.environ.get("WHISPER_MAX_DURATION_SEC", "300"))  # 5 min
MAX_FILE_BYTES = int(os.environ.get("WHISPER_MAX_FILE_BYTES", str(25 * 1024 * 1024)))

ASSEMBLYAI_BASE = "https://api.assemblyai.com/v2"
POLL_INTERVAL_SEC = 2
POLL_TIMEOUT_SEC = 240


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


def _get_api_key() -> str:
    token = os.environ.get("ASSEMBLYAI_API_KEY", "").strip()
    if not token:
        raise RuntimeError(
            "ASSEMBLYAI_API_KEY is not set. Add it to .env (dev) or to your "
            "host's environment variables (prod) to enable transcription."
        )
    return token


def _format_speaker_label(raw: str | None) -> str:
    if raw is None:
        return ""
    s = str(raw).strip()
    if not s:
        return ""
    m = re.match(r"^SPEAKER[_\s-]?(\d+)$", s, flags=re.IGNORECASE)
    if m:
        n = int(m.group(1))
        if 0 <= n < 26:
            return f"Speaker {chr(ord('A') + n)}"
        return f"Speaker {n + 1}"
    if len(s) == 1 and s.isalpha():
        return f"Speaker {s.upper()}"
    return s[:64]


def _upload(path: Path, api_key: str) -> str:
    headers = {"authorization": api_key}
    with path.open("rb") as fh:
        r = requests.post(
            f"{ASSEMBLYAI_BASE}/upload",
            headers=headers,
            data=fh,
            timeout=120,
        )
    r.raise_for_status()
    upload_url = r.json().get("upload_url")
    if not upload_url:
        raise RuntimeError("AssemblyAI upload returned no upload_url.")
    return upload_url


def _request_transcript(audio_url: str, api_key: str) -> str:
    headers = {"authorization": api_key, "content-type": "application/json"}
    # AssemblyAI requires `speech_models` (plural array) on every request.
    # Allowed values per docs: "universal-3-pro", "universal-2".
    raw = (os.environ.get("ASSEMBLYAI_SPEECH_MODELS") or "universal-2").strip()
    speech_models = [m.strip() for m in raw.split(",") if m.strip()]
    body: dict = {
        "audio_url": audio_url,
        "speaker_labels": True,
        "speech_models": speech_models,
    }
    lang = (os.environ.get("WHISPER_LANGUAGE") or "").strip()
    if lang:
        body["language_code"] = lang
    r = requests.post(
        f"{ASSEMBLYAI_BASE}/transcript",
        headers=headers,
        json=body,
        timeout=30,
    )
    if not r.ok:
        try:
            detail = r.json().get("error") or r.text
        except ValueError:
            detail = r.text
        raise RuntimeError(
            f"AssemblyAI rejected the transcript request ({r.status_code}): {detail}"
        )
    transcript_id = r.json().get("id")
    if not transcript_id:
        raise RuntimeError("AssemblyAI did not return a transcript id.")
    return transcript_id


def _poll_transcript(transcript_id: str, api_key: str) -> dict:
    headers = {"authorization": api_key}
    deadline = time.monotonic() + POLL_TIMEOUT_SEC
    while time.monotonic() < deadline:
        r = requests.get(
            f"{ASSEMBLYAI_BASE}/transcript/{transcript_id}",
            headers=headers,
            timeout=30,
        )
        r.raise_for_status()
        data = r.json()
        status = data.get("status")
        if status == "completed":
            return data
        if status == "error":
            raise RuntimeError(
                f"AssemblyAI transcription failed: {data.get('error') or 'unknown error'}"
            )
        time.sleep(POLL_INTERVAL_SEC)
    raise RuntimeError(
        f"AssemblyAI transcription timed out after {POLL_TIMEOUT_SEC}s."
    )


def transcribe_audio_file(path: str) -> tuple[list[tuple[str, str]], float]:
    """
    Transcribe audio at path with AssemblyAI (transcription + speaker diarization).

    Returns (list of (speaker_label, segment_text), duration_seconds).
    speaker_label may be empty if diarization could not assign a speaker.
    """
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

    api_key = _get_api_key()
    upload_url = _upload(p, api_key)
    transcript_id = _request_transcript(upload_url, api_key)
    data = _poll_transcript(transcript_id, api_key)

    rows: list[tuple[str, str]] = []
    utterances = data.get("utterances") or []
    if utterances:
        for u in utterances:
            text = (u.get("text") or "").strip()
            if not text:
                continue
            label = _format_speaker_label(u.get("speaker"))
            rows.append((label, text))
    else:
        # Fallback: no speaker_labels (single speaker / very short clip).
        text = (data.get("text") or "").strip()
        if text:
            rows.append(("", text))

    duration_ms = data.get("audio_duration") or 0
    # AssemblyAI returns seconds in `audio_duration` (despite the name),
    # but defensively handle both seconds and milliseconds.
    duration = float(duration_ms)
    if duration > MAX_AUDIO_DURATION_SEC * 10:  # clearly milliseconds
        duration = duration / 1000.0

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
