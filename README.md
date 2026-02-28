# Echolabs

Early-stage Django app for analyzing conversations with transcripts and feedback notes

## Setup
1) Create and activate a venv (Python 3.11+).
2) Install deps: `pip install -r requirements.txt`
3) Create `.env` from `.env.example` and set `SECRET_KEY`.
4) For Google OAuth, set `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET`.

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

## OAuth setup (allauth)
- Add `Sites` entry in Django admin with your production domain.
- Add a SocialApp for Google with client ID/secret.
- In Google Cloud, add both localhost and production redirect URIs.

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

## A5 – Authentication, OAuth, Public API

All A5 features are implemented and working locally. Production deployment was blocked by a disk quota limit on the PythonAnywhere free tier.

**Implemented:**
- Login/signup pages with username and Google OAuth ("Continue with Google")
- Logout functionality
- All non-home pages and APIs require login (`@login_required` / `LoginRequiredMixin`)
- Navigation hides protected links before login, shows them after
- One public API endpoint (no auth required): `/api/public/conversations/`
- All other APIs protected

**Google OAuth:** configured via `django-allauth`. Redirect URIs set for localhost and production. SocialApp configured in Django admin.

**Vega-Lite:** spec in `group-x-vega-lite-API-demo.txt`, pulls from public API.

**3 public API use cases:** `docs/a5/use_cases/` (Python scripts with descriptions).

## View URLs (A5)
- `/accounts/login/` and `/accounts/signup/`
- Protected: `/conversations/`, `/conversations/analytics/`, `/conversations/chart/`, `/reports/`, `/vega-lite/`, `/external/`
- Protected APIs: `/api/conversations/`, `/api/conversations.txt`, `/api/summary/`
- Public API: `/api/public/conversations/`
