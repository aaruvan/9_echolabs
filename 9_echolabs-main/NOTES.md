# Team Notes (A3 Follow-up)

## What needs attention
- Section 6: JSON API endpoints must return data and we need a screenshot of the JSON output.
- Seed data exists and should make the API work, but it is still blank for me.
- I have physics homework and cannot debug it right now. Please help verify/fix Section 6.

## How to run and test Section 6
1) Activate venv and run migrations:
```
venv\Scripts\activate
python manage.py migrate
```
2) Seed data:
```
python manage.py seed_a3_data
```
3) Run server:
```
python manage.py runserver
```
4) Check JSON API:
```
http://127.0.0.1:8000/api/conversations/
http://127.0.0.1:8000/api/conversations/?q=team
```
5) Screenshot the JSON response in the browser.

## Other deliverables to verify
- A3 screenshots listed in `README.md` exist in `docs/` and are current.
- A2 screenshots still present and match the README.
- If you see missing or outdated docs/images, update them.

## Branching rule
If you are making changes, create a new branch first, work there, and only then merge.
