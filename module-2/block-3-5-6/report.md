# Block 3 — Unified REST API (Django REST Framework)

A single Django project that merges three previous Flask practice exercises
into one REST API built with **DRF** instead of Flask.

## Domains → apps

- `tasks/`   — Domain 1: Task Manager (Practice 21)
  - list with **filtering** (`?status=`, `?priority=`), **search** (`?q=` on title),
    and **custom pagination** (`?page=&limit=`) with the exact `{"tasks":..., "pagination":{...}}` envelope
  - `GET /api/tasks/my/` + `DELETE /api/tasks/<id>/` via a **custom X-User header
    BaseAuthentication / BasePermission** (401 / 403 / 204)
  - `POST /api/tasks/<id>/attachment/` — `MultiPartParser`, server-side extension
    validation (`.txt/.pdf/.png/.jpg`), saved to `MEDIA_ROOT/uploads/`
  - HTML feedback form (`/feedback/`) read through `request.POST`, plus a DRF JSON list
- `notes/`   — Domain 2: Personal Notes (Practice 25)
  - Flask `session` → Django session framework + DRF `SessionAuthentication`
  - `/login/`, `/logout/` (`session.flush()`), `/me/`, `/settings/` (PUT/DELETE)
  - Notes CRUD (DB-backed, keyed to session `username`)
  - **Favorites stored only in the session** — reset on logout (mirrors Flask)
- `library/` — Domain 3: Authors & Books (Practice 27)
  - DRF viewsets, `author_id` FK with `ON DELETE SET NULL`
  - filtering via `django-filter` (`?genre=`, `?author_id=`, case-insensitive `?q=`)
  - tested against **PostgreSQL** (`library_test_db`) in Docker

## Flask → DRF mapping

`request.args` → `request.query_params`; `request.form` → `request.POST` +
template form; `request.files` → `MultiPartParser`; `X-User` header → custom
`BaseAuthentication`/`BasePermission`; Flask `session` → `request.session` +
`SessionAuthentication`.

## Key files

- Settings (incl. `OWNER_FULL_NAME` constant): `config/settings.py`
- Global error envelope `{"error": ...}`: `config/exceptions.py`
- Tests: `conftest.py`, `test_authors.py`, `test_books.py`
- Manual curl checks: `MANUAL_TESTING.md`
- Setup: `README.md`

## Tests

`cd project && pytest -v` → **24 passed** against `library_test_db` (PostgreSQL).
