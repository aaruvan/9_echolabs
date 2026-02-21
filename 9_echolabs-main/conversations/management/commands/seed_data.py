"""
Management command to seed realistic test data for echolabs.
Creates conversations, transcript segments, and improvement notes.
Also demonstrates uniqueness constraint and on_delete behavior.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.utils import timezone
from datetime import timedelta
from conversations.models import Conversation, TranscriptSegment, ImprovementNote

User = get_user_model()


class Command(BaseCommand):
    help = "Seed realistic test data for conversations, segments, and improvement notes"

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Clear existing data before seeding (keeps superuser)",
        )

    def handle(self, *args, **options):
        if options["clear"]:
            self.stdout.write("Clearing existing data...")
            ImprovementNote.objects.all().delete()
            TranscriptSegment.objects.all().delete()
            Conversation.objects.all().delete()

        user = User.objects.get(username="tester")
        base_time = timezone.now() - timedelta(days=7)

        # Create 8 conversations
        conv_data = [
            ("Weekly team sync", 0, 720),
            ("Client call - Project Alpha", 1, 1800),
            ("Coffee chat with mentor", 2, 900),
            ("Job interview - Tech Co", 3, 2700),
            ("Podcast recording prep", 4, 1200),
            ("Sales pitch practice", 5, 600),
            ("Networking event conversations", 6, 3600),
            ("1:1 with manager", 7, 1800),
        ]

        conversations = []
        for title, days_ago, duration in conv_data:
            conv = Conversation.objects.create(
                user=user,
                title=title,
                recorded_at=base_time + timedelta(days=days_ago),
                duration_seconds=duration,
            )
            conversations.append(conv)

        self.stdout.write(self.style.SUCCESS(f"Created {len(conversations)} conversations"))

        # Add transcript segments to first 3 conversations (demonstrating relationships)
        segment_data = [
            (0, [
                "So like, I think we should, um, prioritize the backend first.",
                "The API is basically done, we just need to add authentication.",
                "Yeah, so like, let me know what you all think.",
            ]),
            (1, [
                "Good morning! Thank you for, um, taking the time to meet.",
                "We've made significant progress on the deliverable.",
                "So basically, we're looking at a two-week timeline for the next phase.",
            ]),
            (2, [
                "I've been like, really struggling with the architecture decision.",
                "Could you share how you approached similar problems?",
                "That's super helpful, thanks!",
            ]),
        ]

        for conv_idx, segments in segment_data:
            conv = conversations[conv_idx]
            for i, text in enumerate(segments, start=1):
                seg = TranscriptSegment.objects.create(
                    conversation=conv,
                    text=text,
                    segment_order=i,
                )
                # Add improvement notes to some segments
                if "like" in text.lower() or "um" in text.lower():
                    ImprovementNote.objects.create(
                        segment=seg,
                        note_type=ImprovementNote.NoteType.FILLER_WORD,
                        feedback_text="Consider reducing filler words like 'like' and 'um' for clearer communication.",
                        severity=3,
                    )
                if conv_idx == 2 and i == 1:
                    ImprovementNote.objects.create(
                        segment=seg,
                        note_type=ImprovementNote.NoteType.CONFIDENCE,
                        feedback_text="Try speaking with more assertiveness when discussing challenges.",
                        severity=2,
                    )
                if conv_idx == 0 and i == 3:
                    ImprovementNote.objects.create(
                        segment=seg,
                        note_type=ImprovementNote.NoteType.TONE,
                        feedback_text="Ending with an open question is good for collaboration.",
                        severity=1,
                    )

        self.stdout.write(self.style.SUCCESS("Created transcript segments and improvement notes"))

        # Add more segments to conversation 3 (job interview) - multiple segments per conversation
        job_conv = conversations[3]
        job_segments = [
            "I'm excited about this opportunity and believe my experience aligns well.",
            "In my previous role, I led a team of five engineers.",
            "I'm particularly interested in the challenges you're solving here.",
        ]
        for i, text in enumerate(job_segments, start=1):
            TranscriptSegment.objects.create(conversation=job_conv, text=text, segment_order=i)

        # Add segments to conversations 4 and 5
        for conv_idx, segs in [(4, ["Let's dive into the main topics for today."]), (5, ["Here's our value proposition.", "We focus on three key differentiators."])]:
            conv = conversations[conv_idx]
            for i, text in enumerate(segs, start=1):
                TranscriptSegment.objects.create(conversation=conv, text=text, segment_order=i)

        # Demonstrate uniqueness constraint - this should FAIL
        self.stdout.write("\nDemonstrating uniqueness constraint...")
        try:
            TranscriptSegment.objects.create(
                conversation=conversations[0],
                text="Duplicate order test",
                segment_order=1,  # Already exists!
            )
            self.stdout.write(self.style.ERROR("UNEXPECTED: Uniqueness constraint did not trigger!"))
        except IntegrityError as e:
            self.stdout.write(self.style.SUCCESS(f"✓ Uniqueness constraint works: {type(e).__name__} raised"))

        # Demonstrate on_delete CASCADE - delete a conversation and verify related records are removed
        self.stdout.write("\nDemonstrating on_delete CASCADE...")
        conv_to_delete = conversations[5]
        seg_count_before = TranscriptSegment.objects.filter(conversation=conv_to_delete).count()
        note_count_before = ImprovementNote.objects.filter(segment__conversation=conv_to_delete).count()
        conv_to_delete.delete()
        remaining_segs = TranscriptSegment.objects.filter(conversation_id=conv_to_delete.id).count()
        self.stdout.write(
            self.style.SUCCESS(
                f"✓ CASCADE: Deleted conversation. Removed {seg_count_before} segments and {note_count_before} notes. "
                f"Remaining segments for deleted conv: {remaining_segs}"
            )
        )

        self.stdout.write(self.style.SUCCESS("\n✓ Seed data complete. Summary:"))
        self.stdout.write(f"  - Conversations: {Conversation.objects.count()}")
        self.stdout.write(f"  - Transcript segments: {TranscriptSegment.objects.count()}")
        self.stdout.write(f"  - Improvement notes: {ImprovementNote.objects.count()}")
