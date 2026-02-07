# Echolabs

Early-stage Django app for analyzing conversations with transcripts and feedback notes.

## Setup
1) Create and activate a venv (Python 3.11+).
2) Install deps: `pip install -r requirements.txt`
3) Create `.env` from `.env.example` and set `SECRET_KEY`.

## Run (dev)
```
python manage.py migrate
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
