import csv
import io
import json
import os
from datetime import datetime, timedelta
from django.utils import timezone

import requests
from django.db.models import Count, Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.views.generic import DetailView, ListView

from .models import Conversation, ImprovementNote, TranscriptSegment
from .summarize import summarize_transcript


@login_required
def conversations_manual_view(request):
    conversations = Conversation.objects.all().order_by("-created_at")
    if conversations:
        items = "".join(
            f"<li>{conversation.title} ({conversation.created_at:%Y-%m-%d})</li>"
            for conversation in conversations
        )
        body = f"<ul>{items}</ul>"
    else:
        body = "<p>No conversations yet.</p>"

    html = f"""
    <html>
        <head><title>Conversations (Manual)</title></head>
        <body>
            <h1>Conversations (Manual HttpResponse)</h1>
            {body}
        </body>
    </html>
    """
    return HttpResponse(html)


@login_required
def conversations_render_view(request):
    conversations = Conversation.objects.all().order_by("-created_at")
    context = {"conversations": conversations}
    return render(request, "conversations/conversation_list.html", context)


def home_view(request):
    """Dashboard: recent conversations, metrics, quick insights (Lovable-style)."""
    context = {
        "title": "Echolabs Home",
        "subtitle": "Track conversations, transcripts, and feedback notes.",
    }
    if request.user.is_authenticated:
        today = timezone.now().date()
        conversations = Conversation.objects.filter(user=request.user).order_by("-recorded_at")[:10]
        conversation_count_today = Conversation.objects.filter(user=request.user, recorded_at__date=today).count()
        total_conversations = Conversation.objects.filter(user=request.user).count()
        # Filler count: improvement notes with note_type filler_word (per user's conversations)
        filler_notes = ImprovementNote.objects.filter(
            segment__conversation__user=request.user,
            note_type=ImprovementNote.NoteType.FILLER_WORD,
        )
        filler_total = filler_notes.count()
        avg_filler = round(filler_total / total_conversations, 1) if total_conversations else 0
        # Recent improvement notes for "quick insights" (last 5)
        recent_notes = (
            ImprovementNote.objects.filter(segment__conversation__user=request.user)
            .select_related("segment", "segment__conversation")
            .order_by("-created_at")[:5]
        )
        conv_list = list(Conversation.objects.filter(user=request.user).order_by("-recorded_at")[:10])
        filler_by_conv = {}
        if conv_list:
            ids = [c.id for c in conv_list]
            counts = (
                ImprovementNote.objects.filter(segment__conversation_id__in=ids, note_type=ImprovementNote.NoteType.FILLER_WORD)
                .values("segment__conversation_id")
                .annotate(c=Count("id"))
            )
            filler_by_conv = {r["segment__conversation_id"]: r["c"] for r in counts}
        hour = timezone.now().hour
        if hour < 12:
            greeting = "morning"
        elif hour < 18:
            greeting = "afternoon"
        else:
            greeting = "evening"
        conv_cards = [{"conversation": c, "filler_count": filler_by_conv.get(c.id, 0)} for c in conv_list]
        context.update({
            "conversations": conv_list,
            "conv_cards": conv_cards,
            "conversation_count_today": conversation_count_today,
            "total_conversations": total_conversations,
            "avg_filler": avg_filler,
            "recent_notes": recent_notes,
            "greeting": greeting,
        })
    return render(request, "home.html", context)


class ConversationsBaseView(LoginRequiredMixin, View):
    def get(self, request):
        conversations = Conversation.objects.all().order_by("-created_at")
        context = {"conversations": conversations}
        return render(request, "conversations/conversation_list.html", context)


class ConversationsListView(LoginRequiredMixin, ListView):
    model = Conversation
    template_name = "conversations/conversation_list.html"
    context_object_name = "conversations"

    def get_queryset(self):
        return Conversation.objects.filter(user=self.request.user).order_by("-recorded_at")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        conv_list = list(context["conversations"])
        filler_by_conv = {}
        if conv_list:
            ids = [c.id for c in conv_list]
            counts = (
                ImprovementNote.objects.filter(segment__conversation_id__in=ids, note_type=ImprovementNote.NoteType.FILLER_WORD)
                .values("segment__conversation_id")
                .annotate(c=Count("id"))
            )
            filler_by_conv = {r["segment__conversation_id"]: r["c"] for r in counts}
        context["conv_cards"] = [{"conversation": c, "filler_count": filler_by_conv.get(c.id, 0)} for c in conv_list]
        return context


class ConversationDetailView(LoginRequiredMixin, DetailView):
    model = Conversation
    template_name = "conversations/conversation_detail.html"
    context_object_name = "conversation"

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        conv = context["conversation"]
        notes = ImprovementNote.objects.filter(segment__conversation=conv).select_related("segment").order_by("segment__segment_order", "note_type")
        context["improvement_notes"] = list(notes)
        context["filler_count"] = notes.filter(note_type=ImprovementNote.NoteType.FILLER_WORD).count()
        return context


class ConversationAnalyticsView(LoginRequiredMixin, ListView):
    template_name = "conversations/conversation_analytics.html"
    model = Conversation
    context_object_name = "conversations"

    def get_queryset(self):
        title_query = self.request.GET.get("q", "").strip()
        segment_query = self.request.GET.get("segment", "").strip()

        conversations = Conversation.objects.all()
        if title_query:
            conversations = conversations.filter(title__icontains=title_query)
        if segment_query:
            conversations = conversations.filter(
                segments__text__icontains=segment_query
            ).distinct()
        return conversations

    def post(self, request, *args, **kwargs):
        min_duration = request.POST.get("min_duration", "").strip()
        conversations = Conversation.objects.all()
        if min_duration.isdigit():
            conversations = conversations.filter(duration_seconds__gte=int(min_duration))

        self.object_list = conversations
        context = self.get_context_data(
            object_list=self.object_list,
            title_query="",
            segment_query="",
            min_duration=min_duration,
        )
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        conversations = context["conversations"]

        title_query = kwargs.get("title_query", self.request.GET.get("q", "").strip())
        segment_query = kwargs.get("segment_query", self.request.GET.get("segment", "").strip())
        min_duration = kwargs.get("min_duration", "")

        total_count = conversations.count()
        by_user = (
            conversations.values("user__username")
            .annotate(total=Count("id"))
            .order_by("-total", "user__username")
        )

        context.update(
            {
                "title_query": title_query,
                "segment_query": segment_query,
                "min_duration": min_duration,
                "total_count": total_count,
                "by_user": by_user,
            }
        )
        return context


@login_required
def conversation_chart_png(request):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    rows = (
        Conversation.objects.values("user__username")
        .annotate(total=Count("id"))
        .order_by("-total", "user__username")
    )
    labels = [row["user__username"] or "Unknown" for row in rows]
    values = [row["total"] for row in rows]

    if not labels:
        labels = ["No data"]
        values = [0]

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar(labels, values, color="#2563eb")
    ax.set_title("Conversations by User")
    ax.set_ylabel("Count")
    ax.set_xlabel("User")
    ax.tick_params(axis="x", rotation=20)
    fig.tight_layout()

    buffer = io.BytesIO()
    fig.savefig(buffer, format="png")
    plt.close(fig)
    buffer.seek(0)
    return HttpResponse(buffer.getvalue(), content_type="image/png")


@login_required
def conversation_chart_view(request):
    return render(request, "conversations/conversation_chart.html")


def public_conversations_api_json(request):
    """Public API: no login required. CORS enabled so Vega-Lite editor can fetch data."""
    rows = Conversation.objects.values("user__username").annotate(total=Count("id"))
    data = [
        {
            "user": row["user__username"] or "Unknown",
            "total": row["total"],
        }
        for row in rows
    ]
    response = JsonResponse(data, safe=False)
    response["Access-Control-Allow-Origin"] = "*"
    return response


@login_required
def conversations_api_json(request):
    query = request.GET.get("q", "").strip()
    conversations = Conversation.objects.all()
    if query:
        conversations = conversations.filter(title__icontains=query)

    data = [
        {
            "id": conversation.id,
            "title": conversation.title,
            "recorded_at": conversation.recorded_at.isoformat(),
            "duration_seconds": conversation.duration_seconds,
        }
        for conversation in conversations
    ]
    return JsonResponse(data, safe=False)


@login_required
def conversations_api_text(request):
    query = request.GET.get("q", "").strip()
    conversations = Conversation.objects.all()
    if query:
        conversations = conversations.filter(title__icontains=query)

    lines = ["Conversations API (text/plain)"]
    for conversation in conversations:
        lines.append(f"{conversation.id}: {conversation.title}")
    if len(lines) == 1:
        lines.append("No conversations found.")
    return HttpResponse("\n".join(lines), content_type="text/plain")


@login_required
def api_summary(request):
    """
    Internal JSON API for chart-ready data (e.g. Vega-Lite).
    GET /api/summary/ — returns conversations aggregated by user.
    """
    if request.method != "GET":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    rows = (
        Conversation.objects.values("user__username")
        .annotate(count=Count("id"))
        .order_by("-count", "user__username")
    )
    data = [
        {"username": row["user__username"] or "Unknown", "count": row["count"]}
        for row in rows
    ]
    return JsonResponse(data, safe=False)


def _transcript_for_conversation(conversation):
    """Build full transcript text from conversation segments."""
    segments = conversation.segments.order_by("segment_order")
    return " ".join(s.text for s in segments if s.text)


@login_required
def api_summarize_conversation(request, pk):
    """
    Local LLM: summarize a conversation's transcript using Hugging Face
    bart-large-cnn-samsum (transformers). GET or POST with conversation id.
    """
    if request.method not in ("GET", "POST"):
        return JsonResponse({"error": "Method not allowed"}, status=405)
    conversation = get_object_or_404(Conversation, pk=pk)
    if conversation.user_id != request.user.id:
        return JsonResponse({"error": "Not allowed"}, status=403)
    transcript = _transcript_for_conversation(conversation)
    if not transcript.strip():
        return JsonResponse({"error": "No transcript to summarize", "summary": ""})
    try:
        summary = summarize_transcript(transcript)
        return JsonResponse({"summary": summary})
    except Exception as e:
        return JsonResponse(
            {"error": "Summarization failed", "detail": str(e)},
            status=500,
        )


@login_required
def api_action_items(request):
    """
    External AI: generate action items from conversation text using
    Hugging Face Inference API. POST with conversation_id or text.
    Requires HF_TOKEN in .env for Hugging Face Inference API.
    """
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)
    text = None
    if request.content_type and "application/json" in request.content_type:
        try:
            body = json.loads(request.body)
            conversation_id = body.get("conversation_id")
            text = body.get("text", "").strip()
            if conversation_id and not text:
                conv = get_object_or_404(Conversation, pk=conversation_id)
                if conv.user_id != request.user.id:
                    return JsonResponse({"error": "Not allowed"}, status=403)
                text = _transcript_for_conversation(conv)
        except (ValueError, KeyError):
            pass
    if not text or len(text) > 4000:
        return JsonResponse(
            {"error": "Provide JSON body with conversation_id or text (max 4000 chars)"},
            status=400,
        )
    api_key = os.environ.get("HF_TOKEN") or os.environ.get("HUGGINGFACE_TOKEN")
    if not api_key:
        return JsonResponse(
            {"error": "HF_TOKEN not configured. Add it to .env for Hugging Face Inference API."},
            status=503,
        )
    prompt = f"List 3 action items from the following text in short bullet points:\n\n{text[:2000]}"
    try:
        r = requests.post(
            "https://api-inference.huggingface.co/models/google/flan-t5-base",
            headers={"Authorization": f"Bearer {api_key}"},
            json={"inputs": prompt, "parameters": {"max_new_tokens": 80}},
            timeout=30,
        )
        r.raise_for_status()
        data = r.json()
        if isinstance(data, list) and len(data) and "generated_text" in data[0]:
            action_items = data[0]["generated_text"].strip()
        elif isinstance(data, dict) and "generated_text" in data:
            action_items = data["generated_text"].strip()
        else:
            action_items = str(data) if data else "No action items generated."
        return JsonResponse({"action_items": action_items})
    except requests.RequestException as e:
        return JsonResponse(
            {"error": "External API request failed", "detail": str(e)},
            status=502,
        )


@login_required
def vega_lite_charts_view(request):
    """Page that embeds both Vega-Lite charts (bar + scatter) using data from API URLs."""
    return render(request, "conversations/vega_lite_charts.html")


@login_required
def vega_lite_chart1_png(request):
    """Bar chart as PNG; data from same source as /api/summary/."""
    import vl_convert as vlc

    rows = (
        Conversation.objects.values("user__username")
        .annotate(count=Count("id"))
        .order_by("-count", "user__username")
    )
    data = [
        {"username": row["user__username"] or "Unknown", "count": row["count"]}
        for row in rows
    ]
    spec = {
        "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
        "data": {"values": data},
        "mark": "bar",
        "encoding": {
            "x": {"field": "username", "type": "nominal", "title": "User"},
            "y": {"field": "count", "type": "quantitative", "title": "Count"},
        },
        "title": "Conversations by User",
    }
    png_bytes = vlc.vegalite_to_png(spec)
    return HttpResponse(png_bytes, content_type="image/png")


@login_required
def vega_lite_chart2_jpg(request):
    """Scatter chart as JPEG; data from same source as /api/conversations/."""
    import vl_convert as vlc

    conversations = Conversation.objects.all().order_by("recorded_at")
    data = [
        {
            "recorded_at": c.recorded_at.isoformat(),
            "duration_seconds": c.duration_seconds or 0,
        }
        for c in conversations
    ]
    spec = {
        "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
        "data": {"values": data},
        "mark": "point",
        "encoding": {
            "x": {"field": "recorded_at", "type": "temporal", "title": "Recorded"},
            "y": {"field": "duration_seconds", "type": "quantitative", "title": "Duration (s)"},
        },
        "title": "Duration by Recorded Date",
    }
    png_bytes = vlc.vegalite_to_png(spec)
    from PIL import Image

    img = Image.open(io.BytesIO(png_bytes)).convert("RGB")
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return HttpResponse(buf.getvalue(), content_type="image/jpeg")


@login_required
def external_api_view(request):
    """
    Pull data from an external API (GitHub repo search), combine with internal
    data (conversation count), return template or JSON.
    Query param: ?q= search term (e.g. django).
    """
    q = request.GET.get("q", "").strip()
    wants_json = (
        "application/json" in request.headers.get("Accept", "")
        or request.GET.get("format") == "json"
    )

    internal_count = Conversation.objects.count()

    if not q:
        context = {"error": None, "q": "", "internal_count": internal_count, "repos": []}
        if wants_json:
            return JsonResponse(
                {"error": "Missing query parameter q", "internal_count": internal_count}
            )
        return render(request, "conversations/external_api.html", context)

    try:
        r = requests.get(
            "https://api.github.com/search/repositories",
            params={"q": q, "per_page": 5},
            timeout=5,
        )
        r.raise_for_status()
        data = r.json()
        repos = [
            {
                "name": item.get("full_name", ""),
                "description": (item.get("description") or "")[:200],
                "stars": item.get("stargazers_count", 0),
            }
            for item in data.get("items", [])[:5]
        ]
        error = None
    except requests.RequestException as e:
        repos = []
        error = str(e)
    except (ValueError, KeyError) as e:
        repos = []
        error = f"Unexpected response: {e}"

    combined = {
        "q": q,
        "internal_count": internal_count,
        "repos": repos,
        "error": error,
    }

    if wants_json:
        if error:
            return JsonResponse(combined, status=502)
        return JsonResponse(combined)

    return render(request, "conversations/external_api.html", combined)


@login_required
def export_conversations_csv(request):
    """Download conversations as CSV; timestamped filename, headers, ordered rows."""
    now = datetime.now()
    filename = f"conversations_{now:%Y-%m-%d_%H-%M}.csv"
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = f'attachment; filename="{filename}"'

    writer = csv.writer(response)
    writer.writerow(["id", "user", "title", "recorded_at", "duration_seconds", "created_at"])
    for c in Conversation.objects.all().order_by("-recorded_at"):
        writer.writerow([
            c.id,
            c.user.username if c.user_id else "",
            c.title,
            c.recorded_at.isoformat(),
            c.duration_seconds if c.duration_seconds is not None else "",
            c.created_at.isoformat(),
        ])
    return response


@login_required
def export_conversations_json(request):
    """Download conversations as pretty JSON with metadata and timestamped filename."""
    now = datetime.now()
    filename = f"conversations_{now:%Y-%m-%d_%H-%M}.json"
    qs = Conversation.objects.all().order_by("-recorded_at")
    records = [
        {
            "id": c.id,
            "user": c.user.username if c.user_id else "",
            "title": c.title,
            "recorded_at": c.recorded_at.isoformat(),
            "duration_seconds": c.duration_seconds,
            "created_at": c.created_at.isoformat(),
        }
        for c in qs
    ]
    data = {
        "generated_at": now.isoformat(),
        "record_count": len(records),
        "conversations": records,
    }
    response = JsonResponse(data, json_dumps_params={"indent": 2})
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response


@login_required
def reports_view(request):
    """Reports page: two grouped summaries, totals line, export links."""
    conversations = Conversation.objects.all()
    total_conversations = conversations.count()
    total_segments = TranscriptSegment.objects.count()

    by_user = (
        conversations.values("user__username")
        .annotate(count=Count("id"))
        .order_by("-count", "user__username")
    )
    by_note_type = (
        ImprovementNote.objects.values("note_type")
        .annotate(count=Count("id"))
        .order_by("-count")
    )

    context = {
        "total_conversations": total_conversations,
        "total_segments": total_segments,
        "by_user": by_user,
        "by_note_type": by_note_type,
    }
    return render(request, "conversations/reports.html", context)


@login_required
def progress_view(request):
    """Progress page: stats and charts (conversations + filler over time)."""
    user = request.user
    today = timezone.now().date()
    week_ago = today - timedelta(days=7)
    convs = Conversation.objects.filter(user=user, recorded_at__date__gte=week_ago).order_by("recorded_at__date")
    from django.db.models.functions import TruncDate
    convs_per_day = (
        convs.annotate(day=TruncDate("recorded_at"))
        .values("day")
        .annotate(count=Count("id"))
        .order_by("day")
    )
    filler_per_day = (
        ImprovementNote.objects.filter(
            segment__conversation__user=user,
            note_type=ImprovementNote.NoteType.FILLER_WORD,
            created_at__date__gte=week_ago,
        )
        .annotate(day=TruncDate("created_at"))
        .values("day")
        .annotate(count=Count("id"))
        .order_by("day")
    )
    total_conversations = Conversation.objects.filter(user=user).count()
    total_filler = ImprovementNote.objects.filter(
        segment__conversation__user=user,
        note_type=ImprovementNote.NoteType.FILLER_WORD,
    ).count()
    avg_filler = round(total_filler / total_conversations, 1) if total_conversations else 0
    # Build chart-friendly lists (all 7 days)
    days_order = [week_ago + timedelta(days=i) for i in range(8)]
    conv_by_day = {r["day"]: r["count"] for r in convs_per_day}
    filler_by_day = {r["day"]: r["count"] for r in filler_per_day}
    chart_conversations = [{"date": d.strftime("%a"), "count": conv_by_day.get(d, 0)} for d in days_order]
    chart_filler = [{"date": d.strftime("%a"), "count": filler_by_day.get(d, 0)} for d in days_order]
    max_conv = max((c["count"] for c in chart_conversations), default=0) or 1
    max_filler = max((f["count"] for f in chart_filler), default=0) or 1
    context = {
        "total_conversations": total_conversations,
        "total_filler": total_filler,
        "avg_filler": avg_filler,
        "chart_conversations": chart_conversations,
        "chart_filler": chart_filler,
        "max_conv": max_conv,
        "max_filler": max_filler,
    }
    return render(request, "conversations/progress.html", context)


@login_required
def insights_view(request):
    """Insights page: improvement notes by type, recent notes as cards."""
    user = request.user
    note_type_labels = dict(ImprovementNote.NoteType.choices)
    rows = (
        ImprovementNote.objects.filter(segment__conversation__user=user)
        .values("note_type")
        .annotate(count=Count("id"))
        .order_by("-count")
    )
    by_note_type = [{"note_type": r["note_type"], "count": r["count"], "label": note_type_labels.get(r["note_type"], r["note_type"])} for r in rows]
    recent_notes = (
        ImprovementNote.objects.filter(segment__conversation__user=user)
        .select_related("segment", "segment__conversation")
        .order_by("-created_at")[:12]
    )
    context = {
        "by_note_type": by_note_type,
        "recent_notes": recent_notes,
    }
    return render(request, "conversations/insights.html", context)
