"""
Template tags for auth/oauth. Use is_google_oauth_configured to avoid
showing "Continue with Google" when no SocialApp is set (prevents DoesNotExist).
"""
from django import template
from django.contrib.sites.shortcuts import get_current_site

register = template.Library()


@register.simple_tag(takes_context=True)
def is_google_oauth_configured(context):
    """Return True if a Google SocialApp is configured for the current site."""
    request = context.get("request")
    if not request:
        return False
    try:
        from allauth.socialaccount.models import SocialApp

        site = get_current_site(request)
        return SocialApp.objects.filter(provider="google", sites=site).exists()
    except Exception:
        return False
