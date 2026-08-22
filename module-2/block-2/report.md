- Requests were made via `Postman`.
- CRUD was made by standard `ModelViewSet`
- Filtering was implemented based on `django-filter` library
- Statistics was implemented based on `Pygal` library
- `Tasks` table inherits `ModelMixin` which contains `uuid`, `created_at`, `updated_at` fields.
- Models:
    - `tasks/models.py`
    - `common/models.py` (ModelMixin)
- Router:
    - `todo/urls.py`
    - `tasks/urls.py`
- Logic:
    - `tasks/views.py`






### admin panel:
- username: admin
- password: admin


# Screenshot
### SQLite studio
![image](images/sqlite.webp)

### POST /api/categories/
![image](images/api-categories.webp)

### GET /api/categories/1/tasks/
![image](images/api-categories-tasks.webp)

### GET /api/tasks/stats/
![image](images/api-tasks-stats.webp)

### DELETE /api/tasks/ID/
![image](images/delete-api-tasks.webp)

### GET /api/tasks
![image](images/get-api-tasks.webp)

### GET /api/tasks?status=in_progress
![image](images/get-api-tasks-filter-status.webp)

### GET /api/tasks?priority=high
![image](images/get-api-tasks-filter-priority.webp)

### GET /api/tasks/ID
![image](images/get-by-ID-api-tasks.webp)

### GET /api/tasks/99
![image](images/not-exist-error.webp)

### POST /api/tasks/
![image](images/post-api-tasks.webp)

### PUT /api/tasks/ID
![image](images/put-api-tasks.webp)