web: gunicorn echolabs_project.wsgi:application --workers 2 --timeout 60
release: python manage.py migrate --no-input && python manage.py seed_a10_dashboard
