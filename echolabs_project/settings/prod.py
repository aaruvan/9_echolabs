"""
Production settings.
"""

import os

from .base import *  # noqa: F403

DEBUG = False

# Allow host header from PythonAnywhere (and any env override)
allowed_hosts = os.environ.get("DJANGO_ALLOWED_HOSTS", "")
ALLOWED_HOSTS = [host.strip() for host in allowed_hosts.split(",") if host.strip()]
if not ALLOWED_HOSTS:
    ALLOWED_HOSTS = [".pythonanywhere.com"]
