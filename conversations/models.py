from django.conf import settings
from django.db import models
from django.urls import reverse


class Conversation(models.Model):
    """
    Represents a single recorded conversation/session from the wearable device.
    Each recording belongs to a user and will contain multiple transcript segments.
    This is the primary entity for organizing speech data in echolabs.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="conversations",
    )
    title = models.CharField(max_length=200)
    recorded_at = models.DateTimeField()
    duration_seconds = models.PositiveIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-recorded_at"]

    def __str__(self):
        return f"{self.title} ({self.recorded_at.date()})"

    def get_absolute_url(self):
        return reverse("conversation_detail", kwargs={"pk": self.pk})


class TranscriptSegment(models.Model):
    """
    Represents a single utterance or phrase within a conversation.
    Segments are ordered sequentially and contain the raw text spoken.
    Each segment can have multiple improvement notes attached for feedback.
    """

    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name="segments",
    )
    text = models.TextField()
    segment_order = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["conversation", "segment_order"]
        constraints = [
            models.UniqueConstraint(
                fields=["conversation", "segment_order"],
                name="unique_segment_order_per_conversation",
            )
        ]

    def __str__(self):
        preview = self.text[:50] + "..." if len(self.text) > 50 else self.text
        return f"Segment {self.segment_order}: {preview}"


class ImprovementNote(models.Model):
    """
    Represents feedback or an improvement suggestion for a transcript segment.
    Tracks filler words, confidence, tone, and other speech improvement metrics.
    Multiple notes can exist per segment for different improvement categories.
    """

    class NoteType(models.TextChoices):
        FILLER_WORD = "filler_word", "Filler Word"
        CONFIDENCE = "confidence", "Confidence"
        TONE = "tone", "Tone"
        PACE = "pace", "Pace"
        OTHER = "other", "Other"

    segment = models.ForeignKey(
        TranscriptSegment,
        on_delete=models.CASCADE,
        related_name="improvement_notes",
    )
    note_type = models.CharField(max_length=20, choices=NoteType.choices)
    feedback_text = models.TextField()
    severity = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        help_text="1=low, 5=high",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["segment", "note_type"]

    def __str__(self):
        return f"{self.get_note_type_display()}: {self.feedback_text[:40]}..."
