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


def _create_conversation_with_segments(user, title, recorded_at, duration_seconds, segment_texts):
    """Create one conversation and ordered transcript segments (like ASR chunks)."""
    c = Conversation.objects.create(
        user=user,
        title=title,
        recorded_at=recorded_at,
        duration_seconds=duration_seconds,
    )
    for i, text in enumerate(segment_texts, start=1):
        TranscriptSegment.objects.create(conversation=c, text=text.strip(), segment_order=i)
    return c


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

        # --- tester: multi-turn transcripts (speaker labels + natural speech, segment = utterance) ---
        tester_transcripts = {
            "Team standup recap": [
                "Speaker A: Um, so— yeah, I pushed the auth refactor last night. I'm kinda blocked on the API review though.",
                "Speaker B: Who's supposed to be on that? Jason?",
                "Speaker A: Yeah, but I think he's out. Can we get someone from infra on the sync tomorrow morning?",
                "Speaker B: I'll ping them. If we lock rate limits by Wednesday, Friday beta still sounds doable.",
            ],
            "Client update call": [
                "Speaker A: So they're— they're pretty nervous about the timeline slipping into next month.",
                "Speaker B: Did you tell them we're adding two engineers next sprint?",
                "Speaker A: I did. I said we can still hit the MVP scope we signed off on. They want a written plan by Wednesday and a dashboard demo.",
                "Speaker B: Okay. I'll draft the plan; you line up the demo slot.",
            ],
            "1:1 with manager": [
                "Speaker A: I've been feeling pretty stretched between onboarding the new hire and my own stuff.",
                "Speaker B: Mhm. What do you want to cut or pause?",
                "Speaker A: I'd like to pause the side analytics project until Q3 unless you think that's a bad idea.",
                "Speaker B: No, that works. Your main goal this quarter is still owning the analytics rollout end to end.",
            ],
            "Podcast prep": [
                "Speaker A: For cold open I'm thinking— why conversational AI actually matters for coaching, not just hype.",
                "Speaker B: Then what, three mistakes you see in mock interviews?",
                "Speaker A: Yeah, real examples. I'll keep the main segment under twenty, leave five for Q&A.",
                "Speaker B: Good. Send me the outline before you record.",
            ],
            "Networking chat": [
                "Speaker A: It was really good meeting you at the meetup last week.",
                "Speaker B: Likewise. You said you're looking for a mentor in health tech?",
                "Speaker A: Series B stage, ideally. I'm free Tuesday or Thursday afternoon for coffee if that works.",
                "Speaker B: Thursday works. I'll text you a spot near downtown.",
            ],
        }
        convs_tester = [
            ("Team standup recap", 0, 420),
            ("Client update call", 1, 780),
            ("1:1 with manager", 3, 900),
            ("Podcast prep", 5, 540),
            ("Networking chat", 10, 360),
        ]
        for title, days_ago, duration in convs_tester:
            _create_conversation_with_segments(
                tester,
                title,
                base - day * days_ago,
                duration,
                tester_transcripts[title],
            )

        # --- alex: shorter real transcripts (still turn-taking) ---
        alex_data = [
            (
                "Sprint planning",
                2,
                1200,
                [
                    "Speaker A: Let's pull in the API task first— it's blocking mobile.",
                    "Speaker B: Agreed. I'll move the design polish to next sprint.",
                    "Speaker A: Cool. Velocity was what, forty last sprint?",
                    "Speaker B: Thirty-eight. Let's not overcommit.",
                ],
            ),
            (
                "Design review",
                4,
                600,
                [
                    "Speaker A: The nav feels heavy on mobile. Can we collapse the secondary links?",
                    "Speaker B: Yeah, I can try a hamburger for— for settings only.",
                ],
            ),
            (
                "Stakeholder sync",
                8,
                720,
                [
                    "Speaker A: They want a monthly metrics email, not just the dashboard.",
                    "Speaker B: Fine, but someone has to own the copy.",
                    "Speaker A: Marketing can draft; we automate the numbers.",
                ],
            ),
        ]
        for title, days_ago, duration, segments in alex_data:
            _create_conversation_with_segments(
                alex, title, base - day * days_ago, duration, segments
            )

        # --- sam ---
        sam_data = [
            (
                "Interview debrief",
                0,
                450,
                [
                    "Speaker A: Candidate was strong on system design, a little vague on tradeoffs.",
                    "Speaker B: Did you push on the caching question?",
                    "Speaker A: I did. Answer was okay, not great. I'd lean hire if we need senior IC.",
                ],
            ),
            (
                "Customer discovery",
                2,
                1100,
                [
                    "Speaker A: So walk me through how you run reporting today.",
                    "Speaker B: It's mostly spreadsheets and— and a lot of manual exports from the CRM.",
                    "Speaker A: Where does it hurt the most?",
                    "Speaker B: End of month. Takes like two days to reconcile.",
                ],
            ),
            (
                "Retrospective",
                6,
                660,
                [
                    "Speaker A: What went well?",
                    "Speaker B: Deploy pipeline was smooth.",
                    "Speaker A: What didn't?",
                    "Speaker B: We underestimated the migration. Need better estimates next time.",
                ],
            ),
            (
                "Training session",
                12,
                1800,
                [
                    "Speaker A: Today we're covering the new incident response flow. Questions as we go.",
                    "Speaker B: Is PagerDuty still the source of truth for pages?",
                    "Speaker A: Yes— unless it's a security issue, then you escalate to the hotline in the runbook.",
                ],
            ),
        ]
        for title, days_ago, duration, segments in sam_data:
            _create_conversation_with_segments(
                sam, title, base - day * days_ago, duration, segments
            )

        # --- jordan: transcript + improvement note on a filler-heavy segment ---
        jordan_data = [
            (
                "Quick sync",
                1,
                300,
                [
                    "Speaker A: Just— just checking, are we still aiming for Friday handoff?",
                    "Speaker B: Yeah, unless QA finds something major.",
                ],
            ),
            (
                "Project kickoff",
                7,
                960,
                [
                    "Speaker A: Goals for phase one: auth, basic dashboard, one integration.",
                    "Speaker B: Timeline eight weeks, right?",
                    "Speaker A: That's the target. We'll revisit at week four.",
                ],
            ),
        ]
        for title, days_ago, duration, segments in jordan_data:
            c = _create_conversation_with_segments(
                jordan, title, base - day * days_ago, duration, segments
            )
            if title == "Quick sync":
                seg = TranscriptSegment.objects.filter(conversation=c, segment_order=1).first()
                if seg:
                    ImprovementNote.objects.create(
                        segment=seg,
                        note_type=ImprovementNote.NoteType.FILLER_WORD,
                        feedback_text='Try reducing "just" repeats in quick updates.',
                        severity=1,
                    )

        self.stdout.write(
            self.style.SUCCESS(
                f"Seeded A3/A4 data: 4 users, {Conversation.objects.count()} conversations."
            )
        )
