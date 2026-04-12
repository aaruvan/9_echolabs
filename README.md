# Echolabs

Early-stage Django app for analyzing conversations with transcripts and feedback notes

## Setup
1) Create and activate a venv (Python 3.11+).
2) Install deps: `pip install -r requirements.txt`
3) Create `.env` from `.env.example` and set `SECRET_KEY`.
4) For Google OAuth, set `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET`.

## Checking if Django is installed

**Quick check (any environment):**
```bash
python -c "import django; print(django.__version__)"
```
- If Django is installed you see a version (e.g. `5.0`). If not, you get `ModuleNotFoundError: No module named 'django'`.

**Using pip:**
```bash
pip show django
```
- Shows the installed Django package and path if present; nothing if not installed.

**Important:** Run these in the same environment where you run the app (e.g. after activating your venv). Otherwise you might be checking the system Python instead of the project’s.

## Running locally (rundown)

**1. Activate your virtual environment**

You must use the environment where you installed dependencies (e.g. `requirements.txt`). Otherwise `python`/`pip` may point to system Python and Django won’t be found.

- **macOS/Linux (bash/zsh):**
  ```bash
  source venv/bin/activate
  ```
  or, if you named it differently:
  ```bash
  source .venv/bin/activate
  ```
- **Windows (PowerShell):**
  ```powershell
  .\venv\Scripts\Activate.ps1
  ```
- **Windows (cmd):**
  ```cmd
  venv\Scripts\activate.bat
  ```

When activated, your prompt usually shows `(venv)` or the folder name.

**2. Install dependencies (first time only)**

```bash
pip install -r requirements.txt
```
- Reads `requirements.txt` and installs Django and the other listed packages into the active environment.

**3. Environment variables**

Create a `.env` file (see `.env.example`). At minimum you need:
- `SECRET_KEY` — required by Django (e.g. any long random string for dev).

The app loads these in settings (e.g. via `python-dotenv` or `os.environ`).

**4. Database (first time, or after model changes)**

```bash
python manage.py migrate
```
- Applies migrations: creates/updates the SQLite tables (and other DB objects) to match your models. Run after cloning or after changing `conversations/models.py` (and creating migrations).

**5. Optional: seed data**

```bash
python manage.py seed_a3_data
```
- Loads sample conversations, segments, and improvement notes so you can use the dashboard and detail pages without creating data in the admin. Safe to run more than once (may duplicate data depending on the command).

**6. Sanity check (optional)**

```bash
python manage.py check
```
- Checks project config, URLs, and installed apps. No DB changes. Use this to catch missing env vars or broken settings.

**7. Start the dev server**

```bash
python manage.py runserver
```
- Starts Django’s development server (default: http://127.0.0.1:8000/). Visit that URL in a browser. Stop with `Ctrl+C`.

**Summary (copy-paste for a fresh clone):**
```bash
source venv/bin/activate          # or .venv, or Windows equivalent
pip install -r requirements.txt
cp .env.example .env             # then set SECRET_KEY in .env
python manage.py migrate
python manage.py seed_a3_data    # optional
python manage.py runserver
```

## Run (dev)
```
python manage.py migrate
python manage.py seed_a3_data
python manage.py runserver
```

## Lovable UI (Tailwind CSS)
The app uses a Tailwind-based theme (from the echo-speak-bloom Lovable UI). CSS is built from `assets/`.

**First time:** install Node deps and build:
```bash
cd assets && npm install && npm run build:css && cd ..
```
**After changing templates or `assets/src/input.css`:**
```bash
cd assets && npm run build:css
```
Output is `static/css/lovable.css`. For live rebuilds while editing: `npm run watch:css` (from `assets/`).

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

**Vega-Lite:** spec in `group-9-vega-lite-API-demo.txt`, pulls from public API.

**3 public API use cases:** `docs/a5/use_cases/` (Python scripts with descriptions).

## View URLs (A5)
- `/accounts/login/` and `/accounts/signup/`
- Protected: `/conversations/`, `/conversations/analytics/`, `/conversations/chart/`, `/insights/`, `/progress/`, `/reports/`, `/vega-lite/`, `/external/`
- Protected APIs: `/api/conversations/`, `/api/conversations.txt`, `/api/summary/`
- Public API: `/api/public/conversations/`

## A9 – AI in Django (local + optional API)

- **Local summarization:** conversation detail → “Generate summary” (`/api/summarize/<id>/`). Uses Hugging Face `transformers` (weights download on first use).
- **Optional action items:** same page → Hugging Face Inference API; set `HF_TOKEN` in `.env`.
- **Local semantic coach search:** `/insights/` POST form → `sentence-transformers` retrieval over `conversations/data/coach_knowledge.md`. See [README_AI.md](README_AI.md) for the full workflow and guardrails.
