from django.urls import path

from .views import (
    ConversationsBaseView,
    ConversationsListView,
    conversations_manual_view,
    conversations_render_view,
)

urlpatterns = [
    path("manual/", conversations_manual_view, name="conversations_manual"),
    path("render/", conversations_render_view, name="conversations_render"),
    path("cbv-base/", ConversationsBaseView.as_view(), name="conversations_cbv_base"),
    path("cbv-generic/", ConversationsListView.as_view(), name="conversations_cbv_generic"),
]
