"""
A10 Analytics Dashboard.

Implements the 9 widgets defined in A10 Part 1 across three categories:
    - System Performance (SP-1 segment-count distribution, SP-2 top word counts,
      SP-3 note consistency by length bucket)
    - User Behavior (UB-1 daily usage, UB-2 note-type frequency,
      UB-3 AI adoption rate)
    - Cost (C-1 cost per user, C-2 average cost over time,
      C-3 cost by duration bucket)

Cost is approximated from word count (token-count proxy) using a small
per-token rate so the user sees dollar values that are easy to compare.
"""

from __future__ import annotations

from collections import defaultdict
from datetime import timedelta
from statistics import mean, median

from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.shortcuts import render
from django.utils import timezone

from .models import Conversation, ImprovementNote, TranscriptSegment

# A reasonable proxy price per word so the cost charts read in dollars.
# Roughly equivalent to ~$2 per 1M tokens at ~1.3 tokens/word.
COST_PER_WORD = 0.0000026


def _word_count(text: str) -> int:
    return len(text.split()) if text else 0


def _segment_bucket(seg_count: int) -> str:
    if seg_count < 5:
        return "short (<5)"
    if seg_count <= 10:
        return "medium (5-10)"
    return "long (>10)"


def _duration_bucket(seconds: int | None) -> str:
    d = seconds or 0
    if d < 60:
        return "<60s"
    if d <= 180:
        return "60-180s"
    return ">180s"


def _segment_bucket_order():
    return ["short (<5)", "medium (5-10)", "long (>10)"]


def _duration_bucket_order():
    return ["<60s", "60-180s", ">180s"]


def _build_dashboard_context():
    """Compute every widget's data set in one pass over the data.

    Designed to be cheap on small/medium seed data (a few hundred conversations);
    for production scale this would move to materialized aggregates.
    """
    conversations = list(
        Conversation.objects.select_related("user").prefetch_related("segments").all()
    )
    notes = list(ImprovementNote.objects.select_related("segment__conversation").all())

    note_type_labels = dict(ImprovementNote.NoteType.choices)
    notes_by_conv: dict[int, list[ImprovementNote]] = defaultdict(list)
    for n in notes:
        notes_by_conv[n.segment.conversation_id].append(n)

    per_conv = []
    for c in conversations:
        seg_list = list(c.segments.all())
        seg_count = len(seg_list)
        word_count = sum(_word_count(s.text) for s in seg_list)
        per_conv.append(
            {
                "id": c.id,
                "title": c.title,
                "user": c.user.username if c.user_id else "Unknown",
                "recorded_at": c.recorded_at,
                "duration": c.duration_seconds or 0,
                "segments": seg_count,
                "words": word_count,
                "cost": round(word_count * COST_PER_WORD, 4),
                "note_count": len(notes_by_conv.get(c.id, [])),
                "seg_bucket": _segment_bucket(seg_count),
                "dur_bucket": _duration_bucket(c.duration_seconds),
            }
        )

    # ---------- Headline metrics ----------
    total_conversations = len(conversations)
    total_segments = sum(p["segments"] for p in per_conv)
    total_words = sum(p["words"] for p in per_conv)
    total_cost = round(total_words * COST_PER_WORD, 4)
    total_notes = len(notes)
    unique_users = len({p["user"] for p in per_conv}) if per_conv else 0
    avg_segments = round(mean(p["segments"] for p in per_conv), 1) if per_conv else 0
    avg_cost_per_conv = (
        round(total_cost / total_conversations, 4) if total_conversations else 0
    )

    # ---------- SP-1: Segment-count distribution (histogram) ----------
    sp1_data = [{"segments": p["segments"]} for p in per_conv]

    # ---------- SP-2: Top conversations by word count ----------
    sp2_data = sorted(
        (
            {"label": f"{p['title']} ({p['user']})", "words": p["words"]}
            for p in per_conv
        ),
        key=lambda r: -r["words"],
    )[:10]

    # ---------- SP-3: Avg notes per conversation by segment bucket ----------
    sp3_groups: dict[str, list[int]] = defaultdict(list)
    for p in per_conv:
        sp3_groups[p["seg_bucket"]].append(p["note_count"])
    sp3_data = []
    for bucket in _segment_bucket_order():
        vals = sp3_groups.get(bucket, [])
        sp3_data.append(
            {
                "bucket": bucket,
                "avg_notes": round(mean(vals), 2) if vals else 0,
                "median_notes": round(median(vals), 2) if vals else 0,
                "conversations": len(vals),
            }
        )

    # ---------- UB-1: Conversations per day (last 30 days) ----------
    today = timezone.now().date()
    start_day = today - timedelta(days=29)
    day_counts: dict = {start_day + timedelta(days=i): 0 for i in range(30)}
    for p in per_conv:
        d = p["recorded_at"].date()
        if start_day <= d <= today:
            day_counts[d] = day_counts.get(d, 0) + 1
    ub1_data = [
        {"day": d.isoformat(), "count": v} for d, v in sorted(day_counts.items())
    ]

    # ---------- UB-2: Improvement-note type frequency ----------
    type_counter: dict[str, int] = defaultdict(int)
    for n in notes:
        type_counter[n.note_type] += 1
    ub2_data = sorted(
        (
            {"type": note_type_labels.get(t, t), "count": c}
            for t, c in type_counter.items()
        ),
        key=lambda r: -r["count"],
    )
    if not ub2_data:
        ub2_data = [{"type": "No notes yet", "count": 0}]

    # ---------- UB-3: AI adoption (with vs. without notes) ----------
    with_notes = sum(1 for p in per_conv if p["note_count"] > 0)
    without_notes = total_conversations - with_notes
    ub3_data = [
        {"category": "With AI notes", "count": with_notes},
        {"category": "Without AI notes", "count": without_notes},
    ]

    # ---------- C-1: Cost per user (with note-type breakdown) ----------
    user_words: dict[str, int] = defaultdict(int)
    user_note_words: dict[tuple[str, str], int] = defaultdict(int)
    for p in per_conv:
        user_words[p["user"]] += p["words"]
    # Approximate per-user breakdown by note type using the share of notes per
    # type within a user's conversations. Falls back to "no notes" bucket so
    # users with zero notes still appear.
    user_note_share: dict[str, dict[str, float]] = defaultdict(
        lambda: defaultdict(float)
    )
    for n in notes:
        u = n.segment.conversation.user.username if n.segment.conversation.user_id else "Unknown"
        user_note_share[u][n.note_type] += 1
    c1_data = []
    for user_name, total_w in sorted(user_words.items(), key=lambda kv: -kv[1]):
        cost = total_w * COST_PER_WORD
        breakdown = user_note_share.get(user_name, {})
        if breakdown:
            total_share = sum(breakdown.values()) or 1
            for note_type, share in breakdown.items():
                portion = (share / total_share) * cost
                c1_data.append(
                    {
                        "user": user_name,
                        "note_type": note_type_labels.get(note_type, note_type),
                        "cost": round(portion, 4),
                    }
                )
        else:
            c1_data.append(
                {"user": user_name, "note_type": "No notes", "cost": round(cost, 4)}
            )

    # ---------- C-2: Average cost per conversation per week ----------
    week_groups: dict = defaultdict(list)
    for p in per_conv:
        d = p["recorded_at"].date()
        week_start = d - timedelta(days=d.weekday())
        week_groups[week_start].append(p["cost"])
    c2_data = [
        {
            "week": w.isoformat(),
            "avg_cost": round(mean(vals), 4),
            "conversations": len(vals),
        }
        for w, vals in sorted(week_groups.items())
    ]

    # ---------- C-3: Avg cost by duration bucket ----------
    c3_groups: dict[str, list[float]] = defaultdict(list)
    for p in per_conv:
        c3_groups[p["dur_bucket"]].append(p["cost"])
    c3_data = []
    for bucket in _duration_bucket_order():
        vals = c3_groups.get(bucket, [])
        c3_data.append(
            {
                "bucket": bucket,
                "avg_cost": round(mean(vals), 4) if vals else 0,
                "conversations": len(vals),
            }
        )

    return {
        "metrics": {
            "total_conversations": total_conversations,
            "total_segments": total_segments,
            "total_words": total_words,
            "total_cost": total_cost,
            "total_notes": total_notes,
            "unique_users": unique_users,
            "avg_segments": avg_segments,
            "avg_cost_per_conv": avg_cost_per_conv,
            "cost_per_word": COST_PER_WORD,
        },
        "sp1_data": sp1_data,
        "sp2_data": sp2_data,
        "sp3_data": sp3_data,
        "ub1_data": ub1_data,
        "ub2_data": ub2_data,
        "ub3_data": ub3_data,
        "c1_data": c1_data,
        "c2_data": c2_data,
        "c3_data": c3_data,
    }


@login_required
def a10_dashboard_view(request):
    context = _build_dashboard_context()
    context["page_title"] = "Analytics Dashboard"
    return render(request, "conversations/a10_dashboard.html", context)
