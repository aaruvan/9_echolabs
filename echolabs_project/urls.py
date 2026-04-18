"""
URL configuration for echolabs_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import include, path

from conversations.dashboard import a10_dashboard_view
from conversations.views import (
    api_action_items,
    api_summarize_conversation,
    api_summary,
    conversations_api_json,
    conversations_api_text,
    export_conversations_csv,
    export_conversations_json,
    external_api_view,
    home_view,
    insights_view,
    progress_view,
    public_conversations_api_json,
    reports_view,
    vega_lite_chart1_png,
    vega_lite_chart2_jpg,
    vega_lite_charts_view,
)

urlpatterns = [
    path("", home_view, name="home"),
    path("dashboard/", a10_dashboard_view, name="a10_dashboard"),
    path("admin/", admin.site.urls),
    path("accounts/", include("allauth.urls")),
    path("conversations/", include("conversations.urls")),
    path("progress/", progress_view, name="progress"),
    path("insights/", insights_view, name="insights"),
    path("reports/", reports_view, name="reports"),
    path("reports/export/csv/", export_conversations_csv, name="export_conversations_csv"),
    path("reports/export/json/", export_conversations_json, name="export_conversations_json"),
    path("external/", external_api_view, name="external_api"),
    path("vega-lite/", vega_lite_charts_view, name="vega_lite_charts"),
    path("vega-lite/chart1.png", vega_lite_chart1_png, name="vega_lite_chart1_png"),
    path("vega-lite/chart2.jpg", vega_lite_chart2_jpg, name="vega_lite_chart2_jpg"),
    # API routes
    path("api/summary/", api_summary, name="api_summary"),
    path("api/summarize/<int:pk>/", api_summarize_conversation, name="api_summarize_conversation"),
    path("api/action-items/", api_action_items, name="api_action_items"),
    path("api/conversations/", conversations_api_json, name="conversations_api_json"),
    path(
        "api/conversations.txt",
        conversations_api_text,
        name="conversations_api_text",
    ),
    path(
        "api/public/conversations/",
        public_conversations_api_json,
        name="public_conversations_api_json",
    ),
    path("api/external/", external_api_view, name="api_external"),
]
