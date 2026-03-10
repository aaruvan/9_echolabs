"""
Add transcript segments and improvement notes to existing conversations
that have none. Run on production so Dashboard filler counts and Quick Insights show data.
"""
from django.core.management.base import BaseCommand
from conversations.models import Conversation, TranscriptSegment, ImprovementNote


class Command(BaseCommand):
    help = "Add segments and improvement notes to conversations that have none (for dashboard/insights)."

    def handle(self, *args, **options):
        added_notes = 0
        for conv in Conversation.objects.all():
            segments = list(conv.segments.all().order_by("segment_order"))
            # If only one generic segment (from seed_a3_data), add more content and notes
            if len(segments) <= 1:
                if len(segments) == 0:
                    seg1 = TranscriptSegment.objects.create(
                        conversation=conv,
                        text=f"Opening for {conv.title}. We covered the main points.",
                        segment_order=1,
                    )
                else:
                    seg1 = segments[0]
                # Add a second segment if missing
                if conv.segments.count() < 2:
                    seg2 = TranscriptSegment.objects.create(
                        conversation=conv,
                        text="Follow-up and next steps were discussed.",
                        segment_order=2,
                    )
                else:
                    seg2 = conv.segments.filter(segment_order=2).first()
                # Add improvement notes (so filler count and Quick Insights show)
                if not ImprovementNote.objects.filter(segment=seg1).exists():
                    ImprovementNote.objects.create(
                        segment=seg1,
                        note_type=ImprovementNote.NoteType.FILLER_WORD,
                        feedback_text="Consider reducing filler words like 'um' and 'like' for clearer communication.",
                        severity=2,
                    )
                    added_notes += 1
                if seg2 and not ImprovementNote.objects.filter(segment=seg2).exists():
                    ImprovementNote.objects.create(
                        segment=seg2,
                        note_type=ImprovementNote.NoteType.CONFIDENCE,
                        feedback_text="Good structure. Keep a steady pace when summarizing.",
                        severity=1,
                    )
                    added_notes += 1
        self.stdout.write(
            self.style.SUCCESS(f"Added improvement notes to existing conversations. Total new notes: {added_notes}")
        )
