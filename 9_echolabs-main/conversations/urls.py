from django.urls import path

from .views import (
    ConversationDetailView,
    ConversationAnalyticsView,
    ConversationsBaseView,
    ConversationsListView,
    conversation_chart_png,
    conversation_chart_view,
    conversations_manual_view,
    conversations_render_view,
)

urlpatterns = [
    path("", ConversationsListView.as_view(), name="conversations_list"),
    path("analytics/", ConversationAnalyticsView.as_view(), name="conversation_analytics"),
    path("chart/", conversation_chart_view, name="conversation_chart"),
    path("chart.png", conversation_chart_png, name="conversation_chart_png"),
    path("<int:pk>/", ConversationDetailView.as_view(), name="conversation_detail"),
    path("manual/", conversations_manual_view, name="conversations_manual"),
    path("render/", conversations_render_view, name="conversations_render"),
    path("cbv-base/", ConversationsBaseView.as_view(), name="conversations_cbv_base"),
    path("cbv-generic/", ConversationsListView.as_view(), name="conversations_cbv_generic"),
]
