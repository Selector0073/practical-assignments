# Unified REST API — Django REST Framework

A single Django project that merges three previously separate Flask practice
exercises into one cohesive REST API built with **Django REST Framework (DRF)**:

| Domain          | App       | What it replaces in Flask                    |
|-----------------|-----------|----------------------------------------------|
| Task Manager    | `tasks`   | Practice 21 (task CRUD, feedback, file upload) |
| Personal Notes  | `notes`   | Practice 25 (login, settings, favorites)      |
| Book Library    | `library` | Practice 27 (authors & books)                 |

All Flask request-data idioms are mapped to DRF equivalents:

| Flask                           | DRF / Django                                                              |
|---------------------------------|---------------------------------------------------------------------------|
| `request.args`                  | `request.query_params`                                                    |
| `request.form`                  | Django view reading `request.POST` (populated by the template `<form>`)   |
| `request.files`                 | `MultiPartParser` / `FileUploadParser`                                    |
| custom `X-User` header          | custom `authentication.BaseAuthentication` + `BasePermission`             |
| Flask `session`                 | Django session framework (`request.session`) + DRF `SessionAuthentication` |

The personalization placeholder is a single constant in `config/settings.py`:

```python
OWNER_FULL_NAME = "Your Full Name"   # used for created_by / X-User / welcome msg
OWNER_USERNAME  = "full_name"        # transliterated seeded username
```

---

## Structure

```
project/
  config/                # Django project settings/urls (settings, exceptions, root urls)
  tasks/                 # Domain 1: Task Manager (filter/search/pagination, feedback, upload, X-User)
  notes/                 # Domain 2: Personal Notes + sessions (login, settings, notes, favorites)
  library/               # Domain 3: Authors & Books (testing against PostgreSQL)
  templates/             # (rendered HTML pages)
  conftest.py            # pytest-django fixtures (test_db, client)
  test_authors.py        # 11 tests
  test_books.py          # 13 tests
  pytest.ini
  requirements.txt
  MANUAL_TESTING.md      # curl-style manual verification for Domains 1 & 2
```

---

## Setup

### 1. PostgreSQL (required for the Library domain + tests)

```bash
docker run -d --name library_pg \
  -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=library \
  -p 5432:5432 postgres:17
```

> The conftest automatically detects whether Postgres is reachable on
> `127.0.0.1:5432` (defaults `postgres`/`postgres`) and runs the library tests
> against `library_test_db`. If Postgres is not running it falls back to
> in-memory SQLite so the suite still works anywhere.
> To point elsewhere, export `TEST_DATABASE_URL=postgres://user:pass@host:port/db`.

### 2. Virtual environment & dependencies

```bash
cd project
python3 -m venv ../.venv
source ../.venv/bin/activate
pip install -r requirements.txt
```

### 3. Migrate & run

```bash
python manage.py migrate
python manage.py runserver 127.0.0.1:8000
```

Development settings live in `../.env` (DEBUG / SECRET_KEY), loaded by
`python-dotenv`. Copy `.env.example` if you need a template.

### Seeded users (Domain 2)

| username   | password   |
|------------|------------|
| `full_name`| `secret123`|
| `taras`    | `secret456`|

---

## Endpoints

### Domain 1 — Task Manager (`tasks`)
| Method | URL                              | Notes |
|--------|----------------------------------|-------|
| GET    | `/api/tasks/`                    | filter `?status=`, `?priority=`, search `?q=`, pagination `?page=&limit=` |
| GET    | `/api/tasks/my/`                 | X-User header required (401 if missing) |
| GET    | `/api/tasks/<id>/`               | 404 if missing |
| DELETE | `/api/tasks/<id>/`               | X-User required; owner only (401/403/404/204) |
| POST   | `/api/tasks/<id>/attachment/`    | `-F "file=@..."`; ext `.txt/.pdf/.png/.jpg` (400 otherwise; 404 if task missing) |
| GET    | `/feedback/`                     | HTML form (200) |
| POST   | `/feedback/`                     | form-data submit → 201 on success, 400 on validation |
| GET    | `/api/feedback/`                 | JSON list of feedback |

### Domain 2 — Personal Notes (`notes`)
| Method | URL                              | Notes |
|--------|----------------------------------|-------|
| POST   | `/login/`                        | JSON `{username,password}` → 200/400/401 |
| POST   | `/logout/`                       | flushes session → 200 |
| GET    | `/me/`                           | username + settings → 200/401 |
| PUT    | `/settings/`                     | update only provided `language`/`notes_per_page` |
| DELETE | `/settings/`                     | reset to defaults (uk / 5) |
| POST   | `/api/notes/`                    | create note (title+text required) → 201/400/401 |
| GET    | `/api/notes/`                    | current user's notes → 200/401 |
| DELETE | `/api/notes/<id>/`               | owner only → 204/401/403/404 |
| POST   | `/api/favorites/add/`            | body `{note_id}`; session-scoped |
| DELETE | `/api/favorites/<note_id>/`      | remove from session list |
| GET    | `/api/favorites/`                | full note objects for favorited ids |

Favorites live **only in the session** and reset on logout.

### Domain 3 — Book Library (`library`)
| Method | URL                        | Notes |
|--------|----------------------------|-------|
| GET/POST    | `/api/authors/`            | create requires `name` |
| GET/DELETE  | `/api/authors/<id>/`       | delete keeps books (author_id -> null) |
| GET         | `/api/authors/<id>/books/` | that author's books |
| GET/POST    | `/api/books/`              | create requires `title`, `created_by`; `author_id` validated |
| GET/DELETE  | `/api/books/<id>/`         | |
| filter      | `?genre=`, `?author_id=`, `?q=` (partial title search) |

---

## Running the tests

```bash
cd project
source ../.venv/bin/activate
pytest -v
```

24 tests across `test_authors.py` (11) and `test_books.py` (13) run against
PostgreSQL `library_test_db`. All `created_by` values use `OWNER_FULL_NAME`.

---

## Security notes

* File upload / feedback validation never trusts `Content-Type`; extensions
  are validated **server-side**.
* The HTML feedback form is `@csrf_exempt` by design so it is directly
  curl-testable; in a real deployment prefer keeping CSRF and submitting via
  the rendered template (which already carries `{% csrf_token %}`).
* Session-based auth uses Django's signed session cookies. DRF `SessionAuthentication`
  protects the Notes endpoints; the Library API uses token-free read-only access.
