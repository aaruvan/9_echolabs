from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from conversations.models import Conversation, ImprovementNote, TranscriptSegment

User = get_user_model()


def get_or_create_user(username, email=None):
    user, created = User.objects.get_or_create(
        username=username,
        defaults={"email": email or f"{username}@example.com"},
    )
    if created:
        user.set_unusable_password()
        user.save(update_fields=["password"])
    return user


class Command(BaseCommand):
    help = "Seed sample data for A3/A4: multiple users, varied conversations for better charts."

    def handle(self, *args, **options):
        # Clear existing app data (keep users)
        ImprovementNote.objects.all().delete()
        TranscriptSegment.objects.all().delete()
        Conversation.objects.all().delete()

        base = timezone.now()
        day = timezone.timedelta(days=1)

        # Multiple users so "Conversations by User" bar chart has several bars
        tester = get_or_create_user("tester", "tester@example.com")
        alex = get_or_create_user("alex")
        sam = get_or_create_user("sam")
        jordan = get_or_create_user("jordan")

        # Conversations per user: tester=5, alex=3, sam=4, jordan=2 (varied bar heights)
        # Spread over 2+ weeks with varied durations for a good scatter (duration by date)

        convs_tester = [
            ("Team standup recap", 0, 420),
            ("Client update call", 1, 780),
            ("1:1 with manager", 3, 900),
            ("Podcast prep", 5, 540),
            ("Networking chat", 10, 360),
        ]
        for title, days_ago, duration in convs_tester:
            c = Conversation.objects.create(
                user=tester,
                title=title,
                recorded_at=base - day * days_ago,
                duration_seconds=duration,
            )
            TranscriptSegment.objects.create(
                conversation=c, text=f"Segment for {title}.", segment_order=1
            )

        convs_alex = [
            ("Sprint planning", 2, 1200),
            ("Design review", 4, 600),
            ("Stakeholder sync", 8, 720),
        ]
        for title, days_ago, duration in convs_alex:
            Conversation.objects.create(
                user=alex,
                title=title,
                recorded_at=base - day * days_ago,
                duration_seconds=duration,
            )

        convs_sam = [
            ("Interview debrief", 0, 450),
            ("Customer discovery", 2, 1100),
            ("Retrospective", 6, 660),
            ("Training session", 12, 1800),
        ]
        for title, days_ago, duration in convs_sam:
            Conversation.objects.create(
                user=sam,
                title=title,
                recorded_at=base - day * days_ago,
                duration_seconds=duration,
            )

        convs_jordan = [
            ("Quick sync", 1, 300),
            ("Project kickoff", 7, 960),
        ]
        for title, days_ago, duration in convs_jordan:
            c = Conversation.objects.create(
                user=jordan,
                title=title,
                recorded_at=base - day * days_ago,
                duration_seconds=duration,
            )
            seg = TranscriptSegment.objects.create(
                conversation=c, text="Notes from the meeting.", segment_order=1
            )
            ImprovementNote.objects.create(
                segment=seg,
                note_type=ImprovementNote.NoteType.TONE,
                feedback_text="Clear and professional.",
                severity=1,
            )

        self.stdout.write(
            self.style.SUCCESS(
                f"Seeded A3/A4 data: 4 users, {Conversation.objects.count()} conversations."
            )
        )
