# Echolabs

Early-stage Django app for analyzing conversations with transcripts and feedback notes.

## Setup
1) Create and activate a venv (Python 3.11+).
2) Install deps: `pip install -r requirements.txt`
3) Create `.env` from `.env.example` and set `SECRET_KEY`.

## Run (dev)
```
python manage.py migrate
python manage.py seed_a3_data
python manage.py runserver
```

## Run (prod)
```
$env:DJANGO_SETTINGS_MODULE="echolabs_project.settings.prod"
python manage.py runserver
```

## View URLs (A2)
- `/conversations/manual/`
- `/conversations/render/`
- `/conversations/cbv-base/`
- `/conversations/cbv-generic/`

## Screenshots (A2)
These screenshots demonstrate the required four view types and the template empty/normal states.

- Manual HttpResponse view: `docs/manual-view.png`
- render() view: `docs/render-view.png`
- Base CBV view: `docs/cbv-base-view.png`
- Generic CBV view: `docs/cbv-generic-view.png`

## A3 Overview
The app now includes navigation, detail pages, analytics with GET/POST search, and chart/JSON endpoints.
These features demonstrate model-driven URLs, ORM queries, static styling, and API output.
UI note: styling is loaded from `static/css/styles.css` via Django static files.

## View URLs (A3)
- `/` (home)
- `/conversations/` (list + detail links)
- `/conversations/analytics/` (GET + POST search, aggregates)
- `/conversations/chart/` (chart page) and `/conversations/chart.png` (PNG endpoint)
- `/api/conversations/` (JSON API, supports `?q=`)
- `/api/conversations.txt` (HttpResponse text)

## Screenshots (A3)
- Home page with navigation: `docs/a3-home.png`
- Detail page via list link: `docs/a3-detail.png`
- Analytics page (GET + POST forms + aggregates): `docs/a3-analytics.png`
- Chart page and PNG endpoint: `docs/a3-chart.png`
- JSON API output in browser: `docs/a3-api-json.png`
