"""
Seed five Part 3 evaluation conversations (one transcript scenario each).

Run after migrate; does not delete other users. Safe to re-run: removes prior
conversations with title prefix [Part3] for this user only.

Login: user part3_eval / password part3demo123 (local evaluation only).
"""
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from conversations.models import Conversation, TranscriptSegment

User = get_user_model()

PART3_PREFIX = "[Part3]"


def _create_or_reset_part3_user():
    """Dedicated eval user so graders can follow a fixed script without admin."""
    user, created = User.objects.get_or_create(
        username="part3_eval",
        defaults={"email": "part3_eval@example.com"},
    )
    user.set_password("part3demo123")
    user.save()
    return user


def _replace_part3_conversations(user):
    Conversation.objects.filter(user=user, title__startswith=PART3_PREFIX).delete()


def _add_conversation(user, title, recorded_at, duration_seconds, segment_texts):
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
    help = "Create 5 Part 3 evaluation conversations (transcript scenarios)."

    def handle(self, *args, **options):
        user = _create_or_reset_part3_user()
        _replace_part3_conversations(user)

        base = timezone.now()
        day = timezone.timedelta(days=1)

        # --- TC1: Normal summary (multi-speaker, enough content for BART) ---
        _add_conversation(
            user,
            f"{PART3_PREFIX} Summary — team sync",
            base - day * 0,
            380,
            [
                "Speaker A: Okay, quick standup. I shipped the login flow and the error states are in review.",
                "Speaker B: Nice. Any blockers on the API side?",
                "Speaker A: Yeah, we're waiting on rate limit numbers from infra before we flip the beta flag.",
                "Speaker B: Got it. Let's target Friday for beta if infra can confirm by Wednesday.",
            ],
        )

        # --- TC2: Too-short transcript (summarizer guardrail — should return message, not hallucinate) ---
        _add_conversation(
            user,
            f"{PART3_PREFIX} Summary — too short",
            base - day * 1,
            15,
            [
                "Speaker A: Okay.",
            ],
        )

        # --- TC3: Action items (clear follow-ups for HF Inference action-items button) ---
        _add_conversation(
            user,
            f"{PART3_PREFIX} Action items — project check-in",
            base - day * 2,
            520,
            [
                "Speaker A: Before we wrap, I need three things: send the client the revised timeline by Thursday.",
                "Speaker B: On it.",
                "Speaker A: Second, schedule a 30-minute retro with design for the nav issues.",
                "Speaker B: I'll send a Cal invite today.",
                "Speaker A: Third, post the incident notes in the shared doc so everyone has the same source of truth.",
            ],
        )

        # --- TC4: Coach-facing / interview-style speech (summary + realistic spoken style) ---
        _add_conversation(
            user,
            f"{PART3_PREFIX} Summary — mock interview",
            base - day * 3,
            640,
            [
                "Speaker A: So tell me about a time you disagreed with a teammate.",
                "Speaker B: Um, yeah I— I had a pushback on the rollout plan. I thought we should stage it by region.",
                "Speaker A: How did you handle it?",
                "Speaker B: I brought data from the last launch and suggested a pilot. We compromised on two regions first.",
            ],
        )

        # --- TC5: Retrieval / domain overlap (coach search uses queries, not this transcript; this transcript supports summary + demo overlap with coaching domain) ---
        _add_conversation(
            user,
            f"{PART3_PREFIX} Summary — feedback on pacing",
            base - day * 4,
            480,
            [
                "Speaker A: I noticed you rush through the intro when you're nervous.",
                "Speaker B: Yeah, I tend to speed up when I feel like I'm taking too long.",
                "Speaker A: Try pausing after your first sentence— count to two in your head. It reads as confidence.",
                "Speaker B: I'll practice that. Maybe I can record a short take and watch it back.",
            ],
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"Part 3 eval: user {user.username} / password part3demo123 — "
                f"{Conversation.objects.filter(user=user, title__startswith=PART3_PREFIX).count()} conversations."
            )
        )
