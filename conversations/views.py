import io

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
from django.db.models import Count
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views import View
from django.views.generic import DetailView, ListView

from .models import Conversation


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
