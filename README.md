# FastAPI Notes App - Client Presentation Guide

This document explains the complete project in a way you can present to a client, including architecture, libraries, routes, Docker setup, authentication, filtering/sorting/pagination, and test behavior.

## 1. Project Summary

This is a full-stack FastAPI application for note management with:
- User registration and login
- JWT-based session handling via HTTP-only cookie
- Per-user notes (create, list, toggle done/pending, delete)
- Dashboard UI rendered with Jinja2 templates
- Search, status filter, sorting, and pagination on notes
- PostgreSQL database integration
- Docker and Docker Compose setup
- Automated tests with pytest and FastAPI TestClient

Primary business value:
- Gives each authenticated user a private note board.
- Supports productivity workflows (track pending vs done notes).
- Provides a simple and clean web interface suitable for internal tools or MVP demos.

## 2. Technology Stack

### Backend
- FastAPI: API framework and routing.
- Uvicorn: ASGI server for running FastAPI.
- SQLAlchemy 2.x: ORM for database models and queries.
- psycopg2-binary: PostgreSQL database driver.
- pydantic + pydantic-settings: validation and typed schemas.
- fastapi-pagination: offset/limit pagination helper.

### Security and Auth
- python-jose: JWT token creation and validation.
- passlib[bcrypt] + bcrypt: password hashing and verification.

### Frontend Templating
- Jinja2: server-side HTML rendering.
- Bootstrap 5.3 (CDN): layout and UI components.
- Font Awesome (CDN): icons.
- Google Fonts (Inter): typography.

### Testing
- pytest: test runner.
- fastapi.testclient.TestClient: HTTP test client for endpoints.

### Containerization
- Docker: app image build/runtime.
- Docker Compose: multi-service orchestration (web + postgres).

## 3. Dependency List and Why Each Is Used

From requirements.txt:

- fastapi==0.115.0
  - Core web framework; handles routing, dependency injection, request parsing.

- uvicorn[standard]==0.30.6
  - Runs the ASGI app; `standard` includes performance extras.

- sqlalchemy==2.0.35
  - Defines `User` and `Note` models, sessions, queries, transactions.

- psycopg2-binary==2.9.9
  - PostgreSQL adapter used by SQLAlchemy engine.

- python-dotenv==1.0.1
  - Loads environment variables from `.env`.

- python-jose==3.3.0
  - Encodes/decodes JWT tokens.

- passlib[bcrypt]==1.7.4
  - Password hashing abstraction with bcrypt scheme.

- bcrypt==4.0.1
  - Cryptographic hashing backend for passlib.

- python-multipart==0.0.9
  - Enables parsing HTML form submissions in FastAPI.

- jinja2==3.1.4
  - Template rendering for login/register/dashboard pages.

- email-validator==2.2.0
  - Validates emails used by `EmailStr` in Pydantic schemas.

- pydantic-settings==2.5.2
  - Supports configuration patterns for settings (project uses dotenv + env vars).

- fastapi-pagination==0.12.27
  - Adds paginated responses for note list endpoint logic.

## 4. High-Level Architecture

Request flow:
1. Browser sends HTTP request.
2. FastAPI route receives request.
3. Route resolves dependencies (DB session, current user, query params).
4. Route calls service layer for business logic.
5. Service layer uses SQLAlchemy ORM to query/update PostgreSQL.
6. Route returns either:
   - HTML template response, or
   - redirect response.

Layer responsibilities:
- `routes/`: HTTP handling + request/response wiring.
- `service/`: business rules, validation checks, DB operations.
- `models/`: table definitions and relationships.
- `schemas/`: request/response validation objects.
- `auth/`: password/JWT helper logic.
- `database/`: engine/session setup and dependency.

## 5. Folder-by-Folder Explanation

- `app/main.py`
  - Creates FastAPI app, creates tables on startup, includes routers, enables pagination, redirects `/` to `/login`.

- `app/core/config.py`
  - Loads key env variables (`DATABASE_URL`, `SECRET_KEY`, `DEBUG`).

- `app/database/connection.py`
  - Creates SQLAlchemy engine + sessionmaker.
  - Defines `Base` class for models.
  - Exposes `get_db()` dependency to provide/close DB session per request.

- `app/models/user_model.py`
  - `users` table with UUID primary key.
  - Fields: name, email (unique), password, is_active, created_at.
  - Relationship to notes with cascade delete.

- `app/models/note_model.py`
  - `notes` table with UUID primary key.
  - Fields: title, content, is_done, created_at, user_id.
  - `user_id` foreign key to `users.id`.

- `app/schemas/user_schema.py`
  - Input/output contract for user data.
  - Includes validation (name length, email, minimum password length).

- `app/schemas/note_schema.py`
  - Input/output contract for notes and partial updates.

- `app/auth/password_handler.py`
  - Hash/verify password methods.
  - Truncates passwords to 72 chars before bcrypt to match bcrypt limits.

- `app/auth/jwt_handler.py`
  - JWT create + verify.
  - Reads token from `access_token` cookie and extracts user UUID from `sub` claim.

- `app/service/auth_service.py`
  - Registration: prevent duplicate email, hash password, save user.
  - Login: validate email/password, issue JWT.

- `app/service/note_service.py`
  - Core note operations:
    - `get_all`: user-scoped fetch with search/status filter/sort/order/pagination.
    - `create`: add note.
    - `update`: partial update including toggle done.
    - `delete`: remove note.

- `app/service/user_service.py`
  - Basic user CRUD helpers for `/users` API.

- `app/routes/auth_routes.py`
  - HTML pages and form actions for register/login/logout.
  - Sets/clears auth cookie.

- `app/routes/note_routes.py`
  - Dashboard page and note actions.
  - Uses JWT cookie to identify current user.
  - Supports query params for filtering/sorting and offset pagination.

- `app/routes/user_routes.py`
  - JSON API routes for user create/list/get-by-id.

- `app/template/*.html`
  - `base.html`: global layout and styling.
  - `login.html`: login form.
  - `register.html`: registration form.
  - `dashboard.html`: note CRUD UI + search/filter/sort/pagination controls.

- `test/*.py`
  - Endpoint and DB behavior tests.

## 6. Database Design

### Table: users
- `id`: UUID primary key
- `name`: varchar(50), required
- `email`: varchar(100), unique + indexed, required
- `password`: varchar(255), required
- `is_active`: boolean, default true
- `created_at`: timestamp with timezone, default now

### Table: notes
- `id`: UUID primary key
- `title`: varchar(100), required
- `content`: varchar(500), optional
- `is_done`: boolean, default false
- `created_at`: timestamp with timezone, default now
- `user_id`: UUID foreign key -> users.id, required

Relationship:
- One `User` has many `Note` records.
- Deleting a user cascades and deletes related notes.

## 7. Authentication and Authorization Flow

### Registration
1. User opens `/register` page.
2. Form posts to `POST /register`.
3. Backend validates with `UserCreate` schema.
4. Password is hashed with bcrypt.
5. User row is inserted.
6. App auto-logs in user by issuing JWT.
7. JWT is stored in `access_token` HTTP-only cookie.
8. Redirect to `/dashboard`.

### Login
1. User opens `/login`.
2. Form posts to `POST /login`.
3. Backend verifies email and password hash.
4. JWT issued and saved in HTTP-only cookie.
5. Redirect to `/dashboard`.

### Protected note actions
- Note routes use `get_current_user` logic.
- User ID is extracted from cookie token.
- DB checks ensure note belongs to current user before update/delete.

### Logout
- `GET /logout` deletes auth cookie and redirects to `/login`.

## 8. Route-by-Route Explanation

## Auth Routes

- `GET /register`
  - Returns registration HTML page.

- `POST /register`
  - Creates new user, logs in automatically, sets cookie, redirects to dashboard.
  - On error, re-renders register page with error message.

- `GET /login`
  - Returns login HTML page.

- `POST /login`
  - Validates credentials, sets cookie, redirects to dashboard.
  - On invalid credentials, returns login page with error.

- `GET /logout`
  - Clears auth cookie and redirects to login.

## Note Routes

- `GET /dashboard`
  - Requires valid cookie token.
  - Loads user notes with query options:
    - `search`: text search on note title.
    - `status`: `done` or `pending`.
    - `sort_by`: currently supports model fields (example: `created_at`, `title`, `is_done`).
    - `order`: `asc` or `desc`.
    - `limit` and `offset` for pagination.
  - Returns rendered dashboard page.

- `POST /notes/create`
  - Creates note for current user.
  - Redirects to dashboard.

- `POST /notes/{note_id}/toggle`
  - Flips `is_done` value for owned note.
  - Redirects to dashboard.

- `POST /notes/{note_id}/delete`
  - Deletes owned note.
  - Redirects to dashboard.

## User API Routes

- `POST /users/`
  - Creates user via JSON body.

- `GET /users/`
  - Returns all users.

- `GET /users/{user_id}`
  - Returns single user by UUID.

Important implementation note for presentation:
- `/register` hashes passwords.
- `/users/` creation currently stores password directly from request payload (not hashed). For production, this should be aligned with auth registration flow.

## 9. Dashboard Features (What the Client Sees)

The dashboard supports:
- Add note form (title + optional content)
- List all notes for logged-in user
- Mark note as done/undo
- Delete note
- Search by title
- Filter by status (all/done/pending)
- Sort field selector
- Sort order selector (ascending/descending)
- Pagination with Previous/Next buttons

How sort/search are enabled end-to-end:
- UI sends query params from filter form.
- `GET /dashboard` receives query params.
- Route passes params to `NoteService.get_all`.
- SQLAlchemy query applies filters and ordering.
- Paginated result returns to template.
- Template preserves selected values and query params across pagination links.

## 10. Configuration and Environment Variables

Current env keys used by this project:
- `DATABASE_URL`
- `SECRET_KEY`
- `ACCESS_TOKEN_EXPIRE_MINUTES`
- `ALGORITHM`
- `DEBUG`
- `POSTGRES_USER`
- `POSTGRES_PASSWORD`
- `POSTGRES_DB`

Recommended `.env` example:

```env
DATABASE_URL=postgresql://postgres:root@db:5432/fastapi_db
SECRET_KEY=replace_with_long_random_secret
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
DEBUG=True
POSTGRES_USER=postgres
POSTGRES_PASSWORD=root
POSTGRES_DB=fastapi_db
```

Notes:
- In Docker Compose, DB host should be `db` (service name).
- For local host-only runs (without Docker), host is usually `localhost`.

## 11. Running the Project (Local)

## Prerequisites
- Python 3.11+ (project image uses 3.11)
- PostgreSQL running and reachable by `DATABASE_URL`
- Virtual environment

## Install

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Start server

```bash
uvicorn app.main:app --reload
```

Open in browser:
- http://127.0.0.1:8000

## 12. Docker and Docker Compose Explanation

## Dockerfile

Build logic:
1. `FROM python:3.11-slim`
2. `WORKDIR /app`
3. Copy `requirements.txt`
4. Install dependencies
5. Copy full source
6. Expose port 8000
7. Start Uvicorn with host `0.0.0.0`, port `8000`, `--reload`

Command:

```bash
docker build -t fastapi-learning .
```

Run single container:

```bash
docker run --env-file .env -p 8000:8000 fastapi-learning
```

## docker-compose.yml

Services:
- `web`:
  - Builds app image from current directory.
  - Maps `8000:8000`.
  - Mounts project directory (`.:/app`) for live code updates.
  - Depends on healthy DB container.

- `db`:
  - Uses `postgres:15`.
  - Maps host port `5434` to container `5432`.
  - Persists data in named volume `postgres_data`.
  - Health check via `pg_isready`.

Start stack:

```bash
docker compose up --build
```

Stop stack:

```bash
docker compose down
```

Stop and remove DB volume (danger: deletes DB data):

```bash
docker compose down -v
```

## 13. Testing Guide

Run all tests:

```bash
pytest -q
```

Test files and intent:
- `test/test_conn.py`
  - DB fixture setup, metadata checks, dependency overrides.
- `test/test_auth.py`
  - Register/login/root behavior.
- `test/test_one.py`
  - Integration-like tests for create/list/toggle/delete note flow.
- `test/test_note.py`
  - Route-level tests with monkeypatch and fake services.

Latest observed result:
- Passed: 9

Warnings currently observed:
- Pydantic class-based config deprecation warnings.
- FastAPI `on_event` deprecation warning.
- `datetime.utcnow()` deprecation warning in Python 3.13.

## 14. Security Notes for Client Discussion

Already implemented:
- Password hashing in registration flow.
- HTTP-only cookie for JWT.
- User-scoped note query/update/delete checks.

Recommended improvements before production:
- Add `secure=True` and explicit `samesite` cookie settings.
- Add CSRF protection for form POST routes.
- Hash passwords in `/users/` create route as well.
- Add token expiration handling UX (session timeout message).
- Add rate limiting for auth endpoints.

## 15. Known Limitations and Technical Debt

- Table creation with `Base.metadata.create_all` on app startup is convenient for dev but migration tools (Alembic) are better for production.
- Service and route layers are cleanly separated, but some tests need updates after signature changes.
- No role-based authorization yet (single user role model).
- No edit-note endpoint in UI (only create/toggle/delete).

## 16. Suggested Demo Script for Presentation

1. Open app root -> redirected to login.
2. Register a new account.
3. Show auto-login behavior (dashboard opens).
4. Create 3 notes.
5. Search by note title.
6. Filter by pending/done.
7. Change sort field and order.
8. Toggle one note to done.
9. Delete one note.
10. Show pagination if many notes.
11. Logout and verify access is removed.
12. Explain Docker setup and run `docker compose up --build`.
13. Explain tests and show `pytest -q` summary.

## 17. Quick Command Cheat Sheet

Install dependencies:

```bash
pip install -r requirements.txt
```

Run app (local):

```bash
uvicorn app.main:app --reload
```

Run tests:

```bash
pytest -q
```

Run Docker stack:

```bash
docker compose up --build
```

Stop Docker stack:

```bash
docker compose down
```

