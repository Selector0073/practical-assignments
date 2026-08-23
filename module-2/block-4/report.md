# LibrarySite API Endpoint Report

This API exposes the following routes under the project root. All endpoints are defined in the main URL config and are grouped by resource.

## Base configuration

- Base path: `/api/v1/`
- Authentication: the app uses Django REST Framework with JWT authentication for protected endpoints.
- Authorization rules:
  - `IsLogged`: requires an authenticated user.
  - `IsAdmin`: requires an authenticated user with `is_admin = True`.
  - `CanChangePassword`: allows authenticated users to change their password, unless a reset is pending.

---

## 1) Book endpoints

### 1.1 `GET /api/v1/BookCRUDView/`

Purpose:
- Retrieve one or more books.

Authentication:
- Requires login (`IsLogged`).

Query parameters:
- `id` (optional): filter by book id.

Example:
- `/api/v1/BookCRUDView/?id=3`

Response:
- Returns an array of book objects.
- Each item includes:
  - `id`
  - `title`
  - `img`
  - `reviews`
  - `content`
  - `price`
  - `availability`
  - `reviews_count`
  - `genre`
  - `writed_at`
  - `author`

---

### 1.2 `POST /api/v1/BookCRUDView/`

Purpose:
- Create a new book.

Authentication:
- Requires login (`IsLogged`).

Request body:
- `title`
- `img`
- `reviews`
- `content`
- `price`
- `availability`
- `reviews_count`
- `genre` (category id / foreign key)
- `writed_at` (date)
- `author`

Response:
- Returns the created book serialized with the same fields as above.
- Status: `201 Created`

---

### 1.3 `PUT /api/v1/BookCRUDView/`

Purpose:
- Update an existing book.

Authentication:
- Requires login (`IsLogged`).

Request body:
- `id` (required to identify the book)
- plus the fields to update.

Response:
- Returns the updated book object.

Notes:
- Updates are partial (`partial=True`), so not all fields need to be sent.

---

### 1.4 `DELETE /api/v1/BookCRUDView/`

Purpose:
- Delete a book.

Authentication:
- Requires login (`IsLogged`).

Request body:
- `id` (required)

Response:
- Returns a success message such as:

```json
{ "message": "Book '3' deleted successfully." }
```

- Status: `200 OK`

---

### 1.5 `GET /api/v1/BookPreviewView/`

Purpose:
- Search and preview books by title, genre, and write date.

Authentication:
- Requires login (`IsLogged`).

Query parameters:
- `genre` (optional): filter by genre name.
- `writed_at` (optional): returns books written on or after that date. Expected format: `YYYY-MM-DD`.
- Search term is handled by `SearchFilter` on the `title` field.

Example:
- `/api/v1/BookPreviewView/?search=python`
- `/api/v1/BookPreviewView/?genre=fiction`
- `/api/v1/BookPreviewView/?writed_at=2024-01-01`

Response:
- Returns a list of simplified book objects with:
  - `id`
  - `title`
  - `img`
  - `reviews`
  - `availability`
  - `price`

---

### 1.6 `POST /api/v1/BooksImportView/`

Purpose:
- Import books from the scraper.

Authentication:
- Requires admin privileges (`IsAdmin`).

Behavior:
- Calls the `scrape()` function.
- If the import fails, it returns HTTP `500 Internal Server Error`.

Response:
- No payload is explicitly returned on success.

---

### 1.7 `POST /api/v1/ExportBooksExcelView/`

Purpose:
- Export all books to an Excel file.

Authentication:
- Requires login (`IsLogged`).

Important note:
- The route is configured with a comment indicating `GET`, but the actual implementation is a `post()` method.

Request body:
- It validates incoming data using `BookDetailsSerializer`, although the export is generated from all books in the database.

Response:
- Returns the Excel export response produced by `exportbooksexcel(books)`.

---

## 2) User endpoints

### 2.1 `POST /api/v1/UserCreate/`

Purpose:
- Create a new user account.

Authentication:
- Public, no login required.

Request body:
- `username`
- `email`
- `password`
- `is_admin` (optional; default is `false`)

Behavior:
- Saves the user and hashes the provided password before storing it.

Response:
- Returns the serialized user object.

---

### 2.2 `GET /api/v1/UserCheck/`

Purpose:
- Check user data.

Authentication:
- Requires login (`IsLogged`).

Request behavior:
- The implementation reads `id` from `request.data`, which makes this endpoint effectively tied to a request body rather than query parameters.

Response:
- Returns a filtered list of matching users.

---

### 2.3 `POST /api/v1/UserEmailSendView/`

Purpose:
- Send a password-reset email.

Authentication:
- Public.

Request body:
- Depends on the `reset_password(request.data)` service implementation.

Response:
- Returns the result payload from the password-reset service, with HTTP status from that service.

---

### 2.4 `PUT /api/v1/UserPasswordChangeView/`

Purpose:
- Change the current user password.

Authentication:
- Requires `CanChangePassword` permission.

Behavior:
- The target user is the authenticated user.
- If a new password is supplied, it is hashed before saving.
- If `password_need_reset` is set, it is reset to `false` after the password change.

Request body:
- `password`
- optionally other user fields if needed

Response:
- Returns the updated user object.

---

## 3) JWT authentication endpoints

### 3.1 `POST /api/v1/token/`

Purpose:
- Obtain a JWT access token and refresh token.

Authentication:
- Public.

Request body:
- `username`
- `password`

Response:
- Standard JWT token payload provided by DRF SimpleJWT, typically containing:
  - `access`
  - `refresh`

---

### 3.2 `POST /api/v1/token/refresh/`

Purpose:
- Refresh an expired access token.

Authentication:
- Public.

Request body:
- `refresh`

Response:
- Returns a new `access` token.

---

## 4) Data model summary

### Book

Fields:
- `title`
- `img`
- `reviews`
- `content`
- `price`
- `availability`
- `reviews_count`
- `genre`
- `writed_at`
- `author`

### Category

Fields:
- `genre`

### User

Fields:
- `username`
- `email`
- `password`
- `is_admin`
- `password_need_reset`

---

## 5) Notable implementation details

- `BookCRUDView` is the main CRUD endpoint for books and handles GET, POST, PUT, and DELETE in the same route.
- `BookSearchPreviewView` performs a title search and additional filters by genre and minimum write date.
- `BooksImportView` is limited to admin users.
- `UserCreateView` hashes passwords before saving them.
- `UserPasswordChangeView` also clears the reset flag after a password change.
- There are a few mismatches between comments and actual code:
  - `ExportBooksExcelView` is implemented as `POST`, while the URL comment says `GET`.
  - `UserCheckView` reads `request.data` instead of `request.query_params`, which is unusual for a `GET` route.

