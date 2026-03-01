# After `git pull` on PythonAnywhere

Run these in order (in a **Bash** console on PythonAnywhere, with your project directory and venv active).

## 0. View branches and environments

**Git branches:**
```bash
git branch -a              # list all branches (local + remote)
git branch                 # current branch only
git status                 # current branch and whether up to date
```

**Virtual environments (PythonAnywhere):**  
Web tab → **Virtualenv** section shows the one attached to your app. In Bash, `ls ~/virtualenvs` or `workon` (if using virtualenvwrapper) lists venvs.

## 1. Pull (from A5.2)

```bash
cd ~/echolabs   # or your project path
git fetch origin
git checkout A5.2
git pull origin A5.2
```

## 2. Activate venv (if not already)

```bash
source /home/vanshiaaru/.virtualenvs/echolabs-venv/bin/activate
# or from project dir: source ~/.virtualenvs/echolabs-venv/bin/activate
# or: workon echolabs-venv   (if using virtualenvwrapper)
```

## 3. Install Python deps (only if requirements.txt changed)

```bash
pip install -r requirements.txt
```

## 4. Migrate (safe to run every time)

```bash
python manage.py migrate
```

## 5. Collect static files (required for CSS/JS to load)

```bash
python manage.py collectstatic --noinput
```

This copies everything from `static/` (including `static/css/lovable.css`) into `staticfiles/`, which PythonAnywhere serves.

## 6. Reload the web app

- Open the **Web** tab on PythonAnywhere.
- Click **Reload** for your app (e.g. vanshiaaru.pythonanywhere.com).

---

## Create or reset `tester` user (production only)

Run this once after deploy so login works with `tester` / `uiuc12345`:

```bash
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
u, _ = User.objects.get_or_create(username='tester', defaults={'email': 'tester@example.com'})
u.set_password('uiuc12345')
u.save()
print('tester ready.')
"
```

---

## Important: commit the built CSS

The Lovable theme uses **`static/css/lovable.css`**, which is built by Tailwind. PythonAnywhere doesn’t need Node if that file is **already in the repo**:

- **If you committed `static/css/lovable.css`** → after pull, step 5 (collectstatic) is enough; no need to run Node on the server.
- **If that file is not in the repo** → either commit it after running `cd assets && npm run build:css` locally, or install Node on PythonAnywhere and run the same build there, then run collectstatic.

Quick check: after pulling, run `ls static/css/lovable.css`. If the file exists, you’re good.
