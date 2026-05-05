"""
Production settings.
"""

import os

from .base import *  # noqa: F403

DEBUG = False

allowed_hosts = os.environ.get("DJANGO_ALLOWED_HOSTS", "")
ALLOWED_HOSTS = [host.strip() for host in allowed_hosts.split(",") if host.strip()]
if not ALLOWED_HOSTS:
    ALLOWED_HOSTS = [".onrender.com"]

# Render terminates TLS and forwards X-Forwarded-Proto.
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# Trust the host the request came in on for CSRF (covers Render's *.onrender.com
# subdomain plus any custom host listed in DJANGO_ALLOWED_HOSTS).
CSRF_TRUSTED_ORIGINS = [
    f"https://{h.lstrip('.')}" if h.startswith(".") else f"https://{h}"
    for h in ALLOWED_HOSTS
]
# Cover wildcard-style entries like ".onrender.com" by also trusting the
# wildcard form Django expects.
for h in list(ALLOWED_HOSTS):
    if h.startswith("."):
        CSRF_TRUSTED_ORIGINS.append(f"https://*{h}")
