from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from conversations.models import Conversation, ImprovementNote, TranscriptSegment


class Command(BaseCommand):
    help = "Seed sample data for A3 screenshots."

    def handle(self, *args, **options):
        user_model = get_user_model()
        user, _ = user_model.objects.get_or_create(
            username="tester",
            defaults={"email": "tester@example.com"},
        )

        Conversation.objects.filter(user=user).delete()

        now = timezone.now()
        conv1 = Conversation.objects.create(
            user=user,
            title="Team standup recap",
            recorded_at=now,
            duration_seconds=420,
        )
        conv2 = Conversation.objects.create(
            user=user,
            title="Client update call",
            recorded_at=now - timezone.timedelta(days=1),
            duration_seconds=780,
        )

        seg1 = TranscriptSegment.objects.create(
            conversation=conv1,
            text="We covered sprint goals and blockers.",
            segment_order=1,
        )
        TranscriptSegment.objects.create(
            conversation=conv1,
            text="Next steps are to finalize the UI update.",
            segment_order=2,
        )
        ImprovementNote.objects.create(
            segment=seg1,
            note_type=ImprovementNote.NoteType.CONFIDENCE,
            feedback_text="Good confidence when summarizing.",
            severity=2,
        )

        seg3 = TranscriptSegment.objects.create(
            conversation=conv2,
            text="The client asked about the delivery timeline.",
            segment_order=1,
        )
        ImprovementNote.objects.create(
            segment=seg3,
            note_type=ImprovementNote.NoteType.TONE,
            feedback_text="Maintain a calm tone during questions.",
            severity=3,
        )

        self.stdout.write(self.style.SUCCESS("Seeded A3 sample data."))
