"""
Production settings.

Designed for a slim deployment of the A10 dashboard (Render.com / Heroku /
PythonAnywhere). The app's optional AI / WhisperX features are not required
for the dashboard to render and are loaded lazily — they will only fail if
their pages are visited and the heavy ML deps are missing.
"""

import os

from .base import *  # noqa: F403

DEBUG = os.environ.get("DJANGO_DEBUG", "").lower() in ("1", "true", "yes")

# Allow comma-separated host list via env. Defaults cover Render and
# PythonAnywhere; localhost is always allowed for one-off prod-style tests.
allowed_hosts = os.environ.get("DJANGO_ALLOWED_HOSTS", "")
ALLOWED_HOSTS = [host.strip() for host in allowed_hosts.split(",") if host.strip()]
if not ALLOWED_HOSTS:
    ALLOWED_HOSTS = [".onrender.com", ".pythonanywhere.com"]
ALLOWED_HOSTS += ["localhost", "127.0.0.1"]

# CSRF: trust the platform domains we accept above.
CSRF_TRUSTED_ORIGINS = [
    f"https://{h.lstrip('.')}" if h.startswith(".") else f"https://{h}"
    for h in ALLOWED_HOSTS
    if h not in {"localhost", "127.0.0.1"}
]

# Whitenoise serves the collected static files (CSS, JS) directly from gunicorn.
# It must come *immediately after* SecurityMiddleware.
MIDDLEWARE = list(MIDDLEWARE)  # noqa: F405
if "whitenoise.middleware.WhiteNoiseMiddleware" not in MIDDLEWARE:
    try:
        idx = MIDDLEWARE.index("django.middleware.security.SecurityMiddleware") + 1
    except ValueError:
        idx = 0
    MIDDLEWARE.insert(idx, "whitenoise.middleware.WhiteNoiseMiddleware")

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
WHITENOISE_KEEP_ONLY_HASHED_FILES = True

# Trust the X-Forwarded-Proto header from Render's load balancer so that
# `request.is_secure()` returns True and Django builds https:// URLs correctly.
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# Optional Postgres via DATABASE_URL (Render's managed Postgres add-on).
# Falls back to the SQLite file from base.py when not set, which is fine
# for the dashboard demo since we re-seed on every deploy.
database_url = os.environ.get("DATABASE_URL", "").strip()
if database_url:
    try:
        import dj_database_url

        DATABASES = {
            "default": dj_database_url.parse(
                database_url, conn_max_age=600, ssl_require=True
            )
        }
    except ImportError:
        pass
