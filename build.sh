#!/usr/bin/env bash
# Render build script for the EchoLabs A10 dashboard deployment.
# Installs the slim production requirements (no torch / whisper / transformers),
# collects static files, applies migrations, and seeds the demo dataset
# (including the mohitg2 test user required by A10).
set -o errexit

pip install --upgrade pip
pip install -r requirements-prod.txt

python manage.py collectstatic --no-input
python manage.py migrate --no-input
python manage.py seed_a10_dashboard
