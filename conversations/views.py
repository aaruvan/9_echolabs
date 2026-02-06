from django.http import HttpResponse
from django.shortcuts import render
from django.views import View
from django.views.generic import ListView

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
