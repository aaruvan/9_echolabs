import csv
import io
from datetime import datetime

import requests
from django.db.models import Count
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views import View
from django.views.generic import DetailView, ListView

from .models import Conversation, ImprovementNote, TranscriptSegment


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


def conversations_render_view(request):
    conversations = Conversation.objects.all().order_by("-created_at")
    context = {"conversations": conversations}
    return render(request, "conversations/conversation_list.html", context)


def home_view(request):
    context = {
        "title": "Echolabs Home",
        "subtitle": "Track conversations, transcripts, and feedback notes.",
    }
    return render(request, "home.html", context)


class ConversationsBaseView(View):
    def get(self, request):
        conversations = Conversation.objects.all().order_by("-created_at")
        context = {"conversations": conversations}
        return render(request, "conversations/conversation_list.html", context)


class ConversationsListView(ListView):
    model = Conversation
    template_name = "conversations/conversation_list.html"
    context_object_name = "conversations"

    def get_queryset(self):
        return Conversation.objects.all().order_by("-created_at")


class ConversationDetailView(DetailView):
    model = Conversation
    template_name = "conversations/conversation_detail.html"
    context_object_name = "conversation"


class ConversationAnalyticsView(ListView):
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


def conversation_chart_view(request):
    return render(request, "conversations/conversation_chart.html")


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


def vega_lite_charts_view(request):
    """Page that embeds both Vega-Lite charts (bar + scatter) using data from API URLs."""
    return render(request, "conversations/vega_lite_charts.html")


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
