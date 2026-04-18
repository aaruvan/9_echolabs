"""
Seed simulated data for the A10 Analytics Dashboard.

Generates a few users (including the required ``mohitg2`` test account),
~150 conversations across the past 60 days with realistic transcript
segments and improvement notes. Designed so every widget on
``/dashboard/`` has a non-trivial, interpretable shape:

    * SP-1 histogram: a right-skewed distribution of segment counts.
    * SP-2 horizontal bar: a clear set of "heaviest" conversations.
    * SP-3 bucket comparison: increasing notes for longer conversations.
    * UB-1 daily line: visible day-to-day variation + an upward trend.
    * UB-2 note-type bar: filler words dominate, others trail.
    * UB-3 donut: most conversations have notes, a sizeable minority do not.
    * C-1 stacked cost-per-user: differentiated users.
    * C-2 weekly trend: a slight cost increase over time.
    * C-3 duration buckets: longer durations cost more on average.

Safe to re-run: clears the previous Conversation/Segment/Note rows
before reseeding (does not touch users).
"""

from __future__ import annotations

import random
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from conversations.models import Conversation, ImprovementNote, TranscriptSegment

User = get_user_model()

# ---------------------------------------------------------------------------
# Seed corpus — short, varied utterances we sample to build transcripts.
# ---------------------------------------------------------------------------
SPEAKERS = ["Speaker A", "Speaker B", "Speaker C"]

UTTERANCES = [
    "Um, so I think we should pivot the launch to next quarter.",
    "Yeah, that gives QA enough buffer to actually do the regression sweep.",
    "Honestly, I'm a little nervous about the API stability with this change.",
    "Right, but we can wrap the new endpoints behind a feature flag for now.",
    "Like, the user feedback we got last week was overwhelmingly positive.",
    "Three of the five enterprise customers want SSO before they sign.",
    "Okay, so action item one — Maya owns the SSO spec by Friday.",
    "I'll loop in security to review the threat model on Monday.",
    "Just to recap, we're shipping the dashboard MVP, then iterating on cost.",
    "Cost, latency, retention — those are the three metrics we report weekly.",
    "Pace yourself a bit on this one — you sound rushed.",
    "Try to land the close with a clear ask, not a question.",
    "I keep saying 'kind of' — I should drop that filler.",
    "Speak up at the end of sentences, your tone trails off.",
    "Tone-wise, the apology felt a little defensive — soften that.",
    "Confidence on the technical answer was strong, well done.",
    "Short answer: yes, we can hit the date if scope holds.",
    "Long answer: assuming staging is green by Wednesday morning.",
    "Question — do we want to expose this metric in the public API?",
    "I would not expose it yet, the schema isn't stable enough.",
    "Customer mentioned they evaluated three other vendors before us.",
    "Their main concern was data residency in the EU region.",
    "We can solve that with a Frankfurt deployment in Q3.",
    "Okay, parking that for now — back to the dashboard demo.",
    "The chart on the right needs a clearer title and axis labels.",
    "Yeah, and the empty state should not just be a blank canvas.",
    "Mhm, agreed — let's add a one-line CTA to seed sample data.",
    "I'll cut a ticket for that and assign it to myself.",
    "Last thing — anyone blocking on a review or pairing session?",
    "Nope, I'm good. See everyone Thursday.",
]

CONVERSATION_TITLES = [
    "Weekly product sync",
    "Customer success debrief",
    "Engineering planning",
    "Design critique",
    "Sales enablement training",
    "Roadmap review",
    "Q3 budget walkthrough",
    "Hiring loop debrief",
    "Architecture deep dive",
    "Mock interview practice",
    "Investor update prep",
    "Onboarding 1:1",
    "Town hall rehearsal",
    "Standup",
    "Postmortem: pipeline outage",
    "Brainstorm: pricing tiers",
    "Marketing review",
    "Partner negotiation",
    "Launch readiness check",
    "Office hours with eng",
]

NOTE_TEMPLATES = {
    ImprovementNote.NoteType.FILLER_WORD: [
        "Heard 'um' / 'uh' multiple times in this segment — try a brief pause instead.",
        "Watch for 'kind of' as a hedge; it weakens the statement.",
        "'Just' is showing up a lot — drop it for clarity.",
    ],
    ImprovementNote.NoteType.PACE: [
        "Pace was very fast here; slow down on key numbers.",
        "Long pauses between clauses — try linking the thought.",
    ],
    ImprovementNote.NoteType.TONE: [
        "Tone trailed downward at the end — keep energy on the close.",
        "Sounded apologetic when defending the proposal; lead with the data.",
    ],
    ImprovementNote.NoteType.CONFIDENCE: [
        "Confidence dipped on the technical question — practice the answer.",
        "Strong, clear delivery on the close. Keep this energy.",
    ],
    ImprovementNote.NoteType.OTHER: [
        "Consider summarizing the previous point before moving on.",
        "Open the segment with the headline first, then context.",
    ],
}

# Probability distribution that biases note types so the UB-2 chart has a
# clear winner (filler words) and a long tail.
NOTE_TYPE_WEIGHTS = [
    (ImprovementNote.NoteType.FILLER_WORD, 0.45),
    (ImprovementNote.NoteType.PACE,        0.18),
    (ImprovementNote.NoteType.TONE,        0.15),
    (ImprovementNote.NoteType.CONFIDENCE,  0.13),
    (ImprovementNote.NoteType.OTHER,       0.09),
]


def _weighted_choice(pairs):
    r = random.random()
    cum = 0.0
    for value, weight in pairs:
        cum += weight
        if r <= cum:
            return value
    return pairs[-1][0]


def _make_segments(n_segments: int):
    segments = []
    for _ in range(n_segments):
        speaker = random.choice(SPEAKERS)
        text = random.choice(UTTERANCES)
        # Occasionally combine two utterances to create longer segments
        # (helps SP-2 "top by word count" get clear winners).
        if random.random() < 0.18:
            text = text + " " + random.choice(UTTERANCES)
        segments.append((speaker, text))
    return segments


class Command(BaseCommand):
    help = (
        "Seed simulated data for the A10 dashboard (clears existing "
        "conversations, segments, notes; creates the mohitg2 test user)."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--conversations",
            type=int,
            default=150,
            help="Number of conversations to create (default: 150).",
        )
        parser.add_argument(
            "--days",
            type=int,
            default=60,
            help="Spread conversations across the last N days (default: 60).",
        )
        parser.add_argument(
            "--seed",
            type=int,
            default=42,
            help="RNG seed for reproducible output (default: 42).",
        )

    def handle(self, *args, **options):
        random.seed(options["seed"])
        n_convs = options["conversations"]
        n_days = options["days"]

        self.stdout.write("Clearing existing conversations / segments / notes...")
        ImprovementNote.objects.all().delete()
        TranscriptSegment.objects.all().delete()
        Conversation.objects.all().delete()

        # ---- Users -----------------------------------------------------
        # mohitg2 is the required test account from the assignment brief.
        test_user, created = User.objects.get_or_create(
            username="mohitg2",
            defaults={"email": "mohitg2@illinois.edu"},
        )
        test_user.set_password("uiuc12345")
        test_user.is_staff = True
        test_user.save()
        if created:
            self.stdout.write(self.style.SUCCESS("Created test user mohitg2 / uiuc12345"))
        else:
            self.stdout.write("Reset password on existing test user mohitg2 / uiuc12345")

        other_usernames = ["alex", "sam", "jordan", "priya", "diego"]
        users = [test_user]
        for u in other_usernames:
            user, _ = User.objects.get_or_create(
                username=u, defaults={"email": f"{u}@example.com"}
            )
            user.set_password("uiuc12345")
            user.save()
            users.append(user)

        # User-level cost weights: makes C-1 (cost per user) clearly varied
        # rather than uniform. mohitg2 is the heaviest user.
        user_weights = {
            "mohitg2": 1.6,
            "alex":    1.2,
            "sam":     1.0,
            "jordan":  0.8,
            "priya":   0.9,
            "diego":   0.6,
        }

        now = timezone.now()
        created_convs = 0

        for i in range(n_convs):
            user = random.choices(
                users,
                weights=[user_weights.get(u.username, 1.0) for u in users],
                k=1,
            )[0]

            # Skew time toward the most recent days so UB-1 / C-2 both show
            # a slight upward trend over the 60-day window.
            day_offset = int(random.triangular(0, n_days, n_days * 0.35))
            recorded_at = now - timedelta(
                days=day_offset,
                hours=random.randint(0, 23),
                minutes=random.randint(0, 59),
            )

            # Right-skewed segment count (most conversations are short).
            seg_count = max(2, int(random.lognormvariate(1.6, 0.55)))
            seg_count = min(seg_count, 22)

            # Duration roughly follows segment count (~30s/segment) with noise,
            # then scaled by the user's "talkative" weight so cost-per-user
            # has variance.
            base_per_seg = random.uniform(20, 45)
            duration = int(seg_count * base_per_seg * user_weights.get(user.username, 1.0))

            title = f"{random.choice(CONVERSATION_TITLES)} #{i + 1}"
            conv = Conversation.objects.create(
                user=user,
                title=title,
                recorded_at=recorded_at,
                duration_seconds=duration,
            )

            segs = _make_segments(seg_count)
            seg_objs = []
            for order, (speaker, text) in enumerate(segs, start=1):
                seg_objs.append(
                    TranscriptSegment(
                        conversation=conv,
                        text=text,
                        speaker_label=speaker,
                        segment_order=order,
                    )
                )
            TranscriptSegment.objects.bulk_create(seg_objs)
            seg_objs = list(conv.segments.all())

            # ---- Improvement notes ----------------------------------------
            # Probability of *any* notes scales with conversation length so
            # SP-3 (notes by length bucket) produces a clear monotone trend,
            # and UB-3 (with vs. without notes) lands somewhere around 70/30.
            p_has_notes = min(0.95, 0.35 + seg_count * 0.04)
            if random.random() < p_has_notes:
                # Number of notes scales with segment count.
                n_notes = max(1, int(random.gauss(seg_count * 0.4, 1.0)))
                n_notes = min(n_notes, len(seg_objs) * 2)
                for _ in range(n_notes):
                    seg = random.choice(seg_objs)
                    note_type = _weighted_choice(NOTE_TYPE_WEIGHTS)
                    feedback = random.choice(NOTE_TEMPLATES[note_type])
                    ImprovementNote.objects.create(
                        segment=seg,
                        note_type=note_type,
                        feedback_text=feedback,
                        severity=random.randint(1, 5),
                    )

            created_convs += 1

        total_segments = TranscriptSegment.objects.count()
        total_notes = ImprovementNote.objects.count()
        self.stdout.write(
            self.style.SUCCESS(
                f"Seeded {created_convs} conversations, {total_segments} segments, "
                f"{total_notes} improvement notes across {len(users)} users."
            )
        )
        self.stdout.write(
            self.style.SUCCESS(
                "Login as mohitg2 / uiuc12345 — visit /dashboard/ for the A10 analytics dashboard."
            )
        )
