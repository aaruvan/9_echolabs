"""
Production settings.
"""

import os

from .base import *  # noqa: F403

DEBUG = False

allowed_hosts = os.environ.get("DJANGO_ALLOWED_HOSTS", "")
ALLOWED_HOSTS = [host.strip() for host in allowed_hosts.split(",") if host.strip()]
