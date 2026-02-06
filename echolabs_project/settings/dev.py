"""
Development settings.
"""

from dotenv import load_dotenv

load_dotenv()

from .base import *  # noqa: F403,E402

DEBUG = True

ALLOWED_HOSTS = ["localhost", "127.0.0.1"]
