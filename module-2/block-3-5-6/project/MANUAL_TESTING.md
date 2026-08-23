# Manual testing notes — Unified REST API (Django REST Framework)

This is the curl-style manual verification for Domains 1 & 2 (Tasks + Notes),
mirroring the original Flask curl sequences but adapted to the DRF port/paths.
Automatic tests for Domain 3 (Library) live in `test_authors.py` / `test_books.py`
and are run with `pytest -v`.

## 0. Prereqs

Start Postgres (needed only for the Library tests and full experience):

    docker run -d --name library_pg -e POSTGRES_USER=postgres \
        -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=library -p 5432:5432 postgres:17

Create a venv, install, migrate, seed and run:

    cd project
    python3 -m venv ../.venv
    source ../.venv/bin/activate
    pip install -r requirements.txt
    python manage.py migrate
    python manage.py shell -c "from tasks.models import Task; [Task.objects.create(title=t, description='desc', status=s, priority=p, created_by='Your Full Name') for t,s,p in [('Fix flask bug','todo','low'),('Write report','in_progress','medium'),('Design page','done','high'),('Plan sprint','todo','high')]]"
    python manage.py runserver 127.0.0.1:8000

The `OWNER_FULL_NAME` constant is `"Your Full Name"` and the transliterated
seeded username is `full_name` (password `secret123`). A second seeded user is
`taras` (password `secret456`). Change them in `config/settings.py` if you
prefer a different name.

---

## 1. Domain 1 — Task Manager

### 1.1 Pagination (custom envelope, page/limit)

    curl "http://127.0.0.1:8000/api/tasks/?page=1&limit=2"
    -> {"tasks": [...], "pagination": {"page": 1, "limit": 2, "total": 4, "pages": 2}}

### 1.2 Filter by status / priority (exact match, combinable)

    curl "http://127.0.0.1:8000/api/tasks/?status=todo"
    curl "http://127.0.0.1:8000/api/tasks/?priority=high"
    curl "http://127.0.0.1:8000/api/tasks/?status=todo&q=a&page=1&limit=2"

### 1.3 Case-insensitive partial search on title (q)

    curl "http://127.0.0.1:8000/api/tasks/?q=flask"

### 1.4 X-User header auth — my tasks

    curl "http://127.0.0.1:8000/api/tasks/my/" -H "X-User: Your Full Name"   # 200
    curl -i "http://127.0.0.1:8000/api/tasks/my/"                            # 401 {"error":"Header 'X-User' is required"}

### 1.5 Delete a task (author only)

    curl -X DELETE "http://127.0.0.1:8000/api/tasks/1/" -H "X-User: Your Full Name"   # 204
    curl -X DELETE "http://127.0.0.1:8000/api/tasks/1/"                                # 401
    curl -X DELETE "http://127.0.0.1:8000/api/tasks/1/" -H "X-User: Somebody Else"     # 403 {"error":"You can only delete your own tasks"}
    curl -X DELETE "http://127.0.0.1:8000/api/tasks/999/" -H "X-User: Your Full Name"  # 404

### 1.6 File upload (server-side extension validation)

    printf 'pdf' > report.pdf; printf 'hi' > note.txt
    curl -X POST -F "file=@report.pdf"  http://127.0.0.1:8000/api/tasks/1/attachment/  # 201 {"message":"File uploaded","filename":"report.pdf","content_type":"application/pdf","task_id":1}
    printf 'x' > evil.exe
    curl -X POST -F "file=@evil.exe"     http://127.0.0.1:8000/api/tasks/1/attachment/  # 400
    curl -X POST                          http://127.0.0.1:8000/api/tasks/1/attachment/  # 400 (no file)
    curl -X POST -F "file=@note.txt"     http://127.0.0.1:8000/api/tasks/999/attachment/ # 404

Files land in `project/media/uploads/`. Extension is validated server-side;
a spoofed `Content-Type` is ignored (we trust the server-side ext).

### 1.7 Feedback form (HTML) + JSON list

    curl http://127.0.0.1:8000/feedback/                    # 200 HTML form
    # POST via the rendered HTML form in a browser (the template carries the
    # CSRF token). For curl, the endpoint is csrf_exempt by design:
    curl -X POST http://127.0.0.1:8000/feedback/ -d "name=Ann&email=a@b.com&message=Great"       # 201 HTML confirmation
    curl -X POST http://127.0.0.1:8000/feedback/ -d "name=&email=a@b.com&message="               # 400 (validation)
    curl http://127.0.0.1:8000/api/feedback/                # 200 JSON array

---

## 2. Domain 2 — Personal Notes (Django sessions)

Cookie jars prove session isolation between two users, and that favorites
reset on logout (session-only, exactly like the Flask original).

### 2.1 Login / logout / me

    curl -c /tmp/cookies.txt  -X POST http://127.0.0.1:8000/login/ -H "Content-Type: application/json" -d '{"username":"full_name","password":"secret123"}'
    # -> {"message":"Welcome, Your Full Name!"}
    curl -c /tmp/cookies2.txt -X POST http://127.0.0.1:8000/login/ -H "Content-Type: application/json" -d '{"username":"taras","password":"secret456"}'
    # -> {"message":"Welcome, taras!"}
    curl -b /tmp/cookies.txt http://127.0.0.1:8000/me/
    # -> {"username":"full_name","settings":{"language":"uk","notes_per_page":5}}
    curl -i http://127.0.0.1:8000/me/                        # 401 {"error":"Not logged in"}
    curl -X POST http://127.0.0.1:8000/login/ -H "Content-Type: application/json" -d '{"username":"full_name","password":"wrong"}'  # 401 Invalid credentials
    curl -X POST http://127.0.0.1:8000/logout/               # 200 {"message":"Logged out"}

### 2.2 Settings (session, only provided keys updated)

    curl -b /tmp/cookies.txt -X PUT http://127.0.0.1:8000/settings/ -H "Content-Type: application/json" -d '{"language":"en","notes_per_page":10}'
    # -> {"message":"Settings updated","settings":{"language":"en","notes_per_page":10}}
    curl -b /tmp/cookies.txt http://127.0.0.1:8000/me/       # settings now en/10
    curl -b /tmp/cookies2.txt http://127.0.0.1:8000/me/      # taras still uk/5  (isolation)
    curl -b /tmp/cookies.txt -X DELETE http://127.0.0.1:8000/settings/
    # -> {"message":"Settings reset to defaults","settings":{"language":"uk","notes_per_page":5}}

### 2.3 Notes CRUD

    curl -b /tmp/cookies.txt -X POST http://127.0.0.1:8000/api/notes/ -H "Content-Type: application/json" -d '{"title":"My first note","text":"This is the content"}'
    # -> {"id":1,"title":"My first note","text":"This is the content","author":"full_name"}
    curl -b /tmp/cookies.txt -X POST http://127.0.0.1:8000/api/notes/ -H "Content-Type: application/json" -d '{"text":"no title"}'
    # -> 400 {"error":"field 'title' is required"}
    curl -b /tmp/cookies.txt http://127.0.0.1:8000/api/notes/
    # -> {"notes":[...]}   (only the current user's notes)
    curl -b /tmp/cookies2.txt http://127.0.0.1:8000/api/notes/   # -> {"notes":[]}  (isolation)
    curl -b /tmp/cookies.txt -X DELETE http://127.0.0.1:8000/api/notes/1/   # 204
    curl -b /tmp/cookies2.txt -X DELETE http://127.0.0.1:8000/api/notes/1/   # 404
    # (a taras DELETE of a full_name note, if rebuilt, returns 403)

### 2.4 Favorites (session-only — disappear on logout)

    curl -b /tmp/cookies.txt -X POST http://127.0.0.1:8000/api/favorites/add/ -H "Content-Type: application/json" -d '{"note_id":1}'
    # -> {"message":"Note added to favorites","favorites":[1]}
    curl -b /tmp/cookies.txt -X POST http://127.0.0.1:8000/api/favorites/add/ -H "Content-Type: application/json" -d '{"note_id":1}'
    # -> {"message":"Note already in favorites","favorites":[1]}
    curl -b /tmp/cookies.txt http://127.0.0.1:8000/api/favorites/
    # -> {"favorites":[{"id":1,"title":"...","text":"...","author":"full_name"}]}
    curl -b /tmp/cookies2.txt http://127.0.0.1:8000/api/favorites/   # -> {"favorites":[]} (isolation)
    curl -b /tmp/cookies.txt -X DELETE http://127.0.0.1:8000/api/favorites/1/   # 200 removed
    # Logout wipes favorites (they live in the session, not the DB):
    curl -b /tmp/cookies.txt -X POST http://127.0.0.1:8000/logout/
    curl -i -b /tmp/cookies.txt http://127.0.0.1:8000/api/favorites/   # 401 {error Not logged in}

---

## 3. Domain 3 — Book Library (automated)

Covered by `pytest -v` (24 tests). Quick smoke checks:

    curl http://127.0.0.1:8000/api/authors/
    curl -X POST http://127.0.0.1:8000/api/authors/ -H "Content-Type: application/json" -d '{"name":"Taras Shevchenko","birth_year":1814}'
    curl -X POST http://127.0.0.1:8000/api/books/    -H "Content-Type: application/json" -d '{"title":"Kobzar","genre":"poetry","author_id":1,"created_by":"Your Full Name"}'
    curl "http://127.0.0.1:8000/api/books/?genre=poetry"
    curl "http://127.0.0.1:8000/api/books/?author_id=1"
    curl "http://127.0.0.1:8000/api/books/?q=kobzar"
    curl "http://127.0.0.1:8000/api/authors/1/books/"
    # Deleting an author keeps their books (author_id -> null, ON DELETE SET NULL):
    curl -X DELETE http://127.0.0.1:8000/api/authors/1/
    curl http://127.0.0.1:8000/api/books/1/          # still 200, "author_id": null
