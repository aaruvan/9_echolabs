from pathlib import Path

from django import forms
from django.core.exceptions import ValidationError

from .transcribe import MAX_FILE_BYTES

ALLOWED_AUDIO_EXTENSIONS = frozenset(
    {".wav", ".mp3", ".m4a", ".webm", ".ogg", ".flac", ".mp4", ".mpeg", ".mpga"}
)


class CoachSearchForm(forms.Form):
    """User text query for semantic search over the local coaching knowledge base."""

    query = forms.CharField(
        label="Search coaching tips",
        max_length=500,
        required=False,
        widget=forms.Textarea(
            attrs={
                "rows": 3,
                "class": "w-full rounded-lg border border-border bg-background px-3 py-2 text-sm text-foreground",
                "placeholder": "e.g. How can I reduce filler words before an interview?",
            }
        ),
    )

    def clean_query(self):
        q = (self.cleaned_data.get("query") or "").strip()
        if not q:
            raise forms.ValidationError("Enter a search query.")
        return q


class AudioTranscribeForm(forms.Form):
    """Upload audio for local Whisper transcription (sync, size/duration capped)."""

    title = forms.CharField(
        max_length=200,
        label="Conversation title",
        widget=forms.TextInput(
            attrs={
                "class": "w-full rounded-lg border border-border bg-background px-3 py-2 text-sm text-foreground",
                "placeholder": "e.g. Interview practice — Jan 12",
            }
        ),
    )
    audio = forms.FileField(
        label="Audio file",
        widget=forms.ClearableFileInput(
            attrs={
                "class": "block w-full text-sm text-muted-foreground file:mr-4 file:rounded-lg file:border-0 file:bg-primary file:px-4 file:py-2 file:text-sm file:font-medium file:text-primary-foreground",
                "accept": "audio/*,.mp4,.mpeg,.mpga",
            }
        ),
    )

    def clean_audio(self):
        f = self.cleaned_data.get("audio")
        if not f:
            raise ValidationError("Choose an audio file.")
        ext = Path(f.name).suffix.lower()
        if ext not in ALLOWED_AUDIO_EXTENSIONS:
            raise ValidationError(
                "Unsupported format. Allowed: "
                + ", ".join(sorted(ALLOWED_AUDIO_EXTENSIONS))
                + "."
            )
        if f.size > MAX_FILE_BYTES:
            raise ValidationError(
                f"File too large (max {MAX_FILE_BYTES // (1024 * 1024)} MB)."
            )
        return f
