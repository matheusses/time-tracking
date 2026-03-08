# time-tracking

A modular monolith time-tracking application built with **Django 5.2+**, **PostgreSQL**, **HTMX**, and **Tailwind CSS**. It uses a layered architecture (presentation → use cases → domain services → infrastructure) as described in [docs/adr/architectural_decision.md](docs/adr/architectural_decision.md).

## Project overview and purpose

- **Track time** with an active timer (single running timer per user). Start/stop from the home page via HTMX; optional project and task-type dropdowns (scoped by user's client). The **first project is selected by default** when options are available.
- **Weekly timesheet**: view time aggregated by project and task type per day; navigate weeks (prev/next) with HTMX partial updates; inline-edit hours in any cell (manual entry or adjustment). The weekly timesheet is **embedded on the tracking (home) page** and also available at `/timesheet/`. By default the grid is **read-only**; use **Edit** to enable cell edits, then **Save** (to persist and return to read-only) or **Cancel** (to discard and return to read-only). Implemented in `tracking`: `TimesheetService`, `GenerateWeeklyTimesheetUseCase`, `UpdateTimeEntryUseCase`, and HTMX views/partials.
- **Project & client management** (see below): clients, projects, and task types live in the `project_management` app. Admin manages them and assigns each user to a client; non-admin users only see options for their client.

The codebase follows clean layering: views call use cases, use cases call domain services, and only domain services use the Django ORM.

---

## Setup and installation

### Prerequisites

- Python 3.12+
- PostgreSQL 14+
- (Optional) Docker and Docker Compose for containerized run

### Local setup

1. **Clone and enter the repo**

   ```bash
   git clone <repo-url>
   cd time-tracking
   ```

2. **Create a virtual environment and install dependencies**

   ```bash
   python -m venv .venv
   source .venv/bin/activate   # Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

   **Important:** Always activate the venv before running `manage.py` or using the project. If you use **pyenv**, the repo includes a `.python-version` (3.11.11) so `python` in this directory uses that version; the venv still needs to be activated (or use `.venv/bin/python`). In **Cursor/VS Code**, set the Python interpreter to `.venv/bin/python` so Run/Debug and the terminal use the venv (Command Palette → "Python: Select Interpreter").

3. **Configure environment**

   ```bash
   cp .env.example .env
   # Edit .env: set DJANGO_SECRET_KEY, DATABASE_URL (or PGHOST/PGDATABASE/PGUSER/PGPASSWORD)
   ```

4. **Create the database and run migrations**

   ```bash
   createdb timetracking   # if using local PostgreSQL
   python manage.py migrate
   ```

5. **Create a superuser (optional)**

   ```bash
   python manage.py createsuperuser
   ```

---

## Troubleshooting

- **"Couldn't import Django" / `ModuleNotFoundError: No module named 'django'`**  
  The interpreter running the code is not the project’s virtual environment. Fix: activate the venv (`source .venv/bin/activate`) in the terminal, or in Cursor/VS Code choose **Python: Select Interpreter** and pick `.venv/bin/python`.

- **`OperationalError: password authentication failed for user "postgres"`**  
  The password in `.env` does not match the one PostgreSQL expects.  
  - **Using Docker for Postgres:** Start the DB with `docker compose up -d db` (or `docker compose -f docker-compose-debug.yml up -d db`). Ensure `.env` has `PGPASSWORD=postgres` (or the same value you used when the volume was first created). If you changed the password after creating the volume, either use the original password in `.env` or recreate the volume: `docker compose down -v` then `docker compose up -d db`.  
  - **Using a local PostgreSQL:** Set in `.env` the same password the `postgres` user has (e.g. `DATABASE_URL=postgresql://postgres:YOUR_ACTUAL_PASSWORD@localhost:5432/timetracking` or `PGPASSWORD=YOUR_ACTUAL_PASSWORD`). To change the DB user password: `psql -U postgres -c "ALTER USER postgres PASSWORD 'postgres';"` (or your chosen password).

---

## Core time tracking (single-timer rule)

- **One active timer per user**: starting a new timer automatically stops any existing running timer for that user.
- **Flow**: User clicks "Start timer" → view calls `StartTimerUseCase` → `TimerService` stops any active timer, then creates a new `TimeEntry` with `ended_at=None`. User clicks "Stop" → `StopTimerUseCase` → `TimerService` sets `ended_at=now()` and returns duration.
- **Layers**: Views (HTMX) → use cases → `TimerService` → Django ORM. All DB access for timers is in `tracking.domain.services.timer_service.TimerService`.

---

## Weekly timesheet

- **Routes**: Embedded on the **home page** (`/`) and standalone at **`/timesheet/`** (optional `?week=YYYY-Www`, e.g. `2025-W10`). Requires login.
- **Behavior**: One optimized query loads all time entries for the week; grid shows rows (project × task type) and columns (Mon–Sun). Previous/Next week use HTMX to swap only the grid (no full-page reload). The grid is **read-only by default**; click **Edit** to enable inline editing, then **Save** (persist and return to read-only) or **Cancel** (discard and return to read-only). In edit mode, each cell is an inline-editable hours field; on change, HTMX POSTs to `/timesheet/update/` and the cell is replaced with the updated value.
- **Manual hours**: Time entries can have an optional `manual_duration_seconds` (e.g. for manual log or adjustment). Timer entries and manual entries for the same (user, date, project, task) are summed in the cell.
- **Manual entry**: The grid includes a row for every (project × task type) combination (from the user’s available projects and global task types), so users can add hours in any cell even when no entry exists for that day; submitting creates a new manual time entry. Editing an existing cell updates the manual entry or creates one. See [Manual entry and validation](docs/manual-entry.md).
- **Validation**: Hours must be non-negative; `project_id` and `task_type_id` (when provided) must exist. Invalid input returns the same cell partial with an error message (no full-page reload).
- **Layers**: `tracking.views.timesheet_views` → `GenerateWeeklyTimesheetUseCase` / `UpdateTimeEntryUseCase` → `TimesheetService` → ORM.

---

## Project & client management

- **Hierarchy**: Client → Project. Task types are global (e.g. Design, Development, Meeting). Implemented in the **project_management** app.
- **Admin**: Full CRUD on Client, Project, and Task Type in Django Admin. Each user can be associated with one client via the User edit form (UserProfile inline); admin assigns this.
- **Non-admin**: No CRUD on clients/projects. Timer and timesheet dropdowns (project, task type) are **read-only** and scoped by the user's associated client (staff see all).
- **Layers**: Options for the timer come from `project_management.use_cases.get_timer_options` → `ProjectService`; views do not use the ORM directly.
- **Security**: Client/Project/Task Type CRUD is admin-only. Non-admin users cannot access management UIs or APIs; they only receive scoped read-only options for the timer/timesheet.

---

## Usage examples

- **Run the development server (local)**

  ```bash
  python manage.py runserver
  ```

  Then open http://127.0.0.1:8000/  
  Log in at http://127.0.0.1:8000/accounts/login/ (use a user created with `createsuperuser` or another user you have created).

- **Run with Docker Compose (app + PostgreSQL)**

  ```bash
  docker compose up --build
  ```

  App: http://localhost:8000/ (ensure `DJANGO_ALLOWED_HOSTS` includes `localhost` in the Compose env).

- **Run in debug/development mode with volume mounts**

  ```bash
  docker compose -f docker-compose-debug.yml up --build
  ```

  Use this for live code reload and optional debugger port. See [Docker and debug Compose](#docker-and-debug-compose) below.

- **Run tests**

  ```bash
  python manage.py test
  ```

  In Docker:

  ```bash
  docker compose run --rm app python manage.py test
  ```

---

## Testing instructions

- **Run all tests (Django test runner)**

  ```bash
  python manage.py test
  ```

- **Run only the core test suite** (unit, integration, functional under `core/tests/`)

  ```bash
  python manage.py test core.tests
  ```

- **Run with pytest** (optional; install `pytest-django` first)

  ```bash
  pip install pytest-django
  pytest
  ```

  Configuration is in `pytest.ini`; test discovery includes `core/tests`, `tracking/tests`, and `project_management/tests`.

- **With coverage (optional)**

  ```bash
  pip install coverage
  coverage run --source=. manage.py test
  coverage report
  ```

When `DATABASE_URL` and `PGPASSWORD` are not set, tests use an in-memory SQLite database so they run without a local PostgreSQL instance. With Postgres env set, tests use PostgreSQL.

Tests should be added for any new or modified code (unit at minimum; integration when touching DB/APIs/auth). See [docs/tasks/09-tests.md](docs/tasks/09-tests.md) for the test strategy and checklist.

### Security test checklist (OWASP-aligned)

The test suite includes security-focused tests in `core/tests/functional/test_security.py`. Checklist covered:

| Area | What is tested |
|------|-----------------|
| **A01:2021 – Broken Access Control** | Unauthenticated access to timer/timesheet endpoints redirects to login; user data isolation (one user cannot see another’s entries). |
| **A02:2021 – Cryptographic Failures** | Secrets and DB URLs come from environment (see Security considerations). |
| **A05:2021 – Security Misconfiguration** | DEBUG and ALLOWED_HOSTS guidance in README and deployment checklist. |
| **A07:2021 – Identification and Authentication Failures** | Login required for protected views; invalid credentials return error. |
| **CSRF** | POST to timer start/stop and timesheet update without valid CSRF token returns 403. |
| **Input validation** | Invalid date or missing required fields on timesheet update return 400; invalid project/task_type raise validation errors. |
| **Method restrictions** | Timesheet update endpoint accepts only POST (GET returns 405). |

Run security-related tests: `python manage.py test core.tests.functional.test_security`.

---

## Security considerations

- **Secrets**: Never commit `.env`. Use `DJANGO_SECRET_KEY` and `DATABASE_URL` (or equivalent) from the environment. Rotate secrets in production.
- **OWASP alignment**: Input validation and sanitization at boundaries; CSRF and XSS protections (Django defaults); use ORM/parameterized queries to avoid SQL injection.
- **Authentication**: Use Django auth; protect admin and sensitive views; enforce strong passwords via `AUTH_PASSWORD_VALIDATORS`. A login page is available at `/accounts/login/`; after login users are redirected to the home page. Timer and timesheet views require an authenticated user.
- **Production**: Set `DEBUG=false`, restrict `ALLOWED_HOSTS`, use HTTPS, and follow [Django deployment checklist](https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/).

**Security contact**: Report vulnerabilities privately to the maintainers (see CODEOWNERS); do not open public issues for security-sensitive findings.

- ⚠️ **Security risks**: Default/weak secrets, exposed debug mode, or misconfigured `ALLOWED_HOSTS` can lead to information disclosure or abuse.
- ✅ **Suggested mitigations**: Use strong `DJANGO_SECRET_KEY` from env; set `DJANGO_DEBUG=false` in production; limit `DJANGO_ALLOWED_HOSTS`; run dependency and secret scanning in CI.

---

## Docker and debug Compose

- **Dockerfile**: Multi-stage build; final stage runs as non-root, runs the app (e.g. gunicorn/uvicorn).
- **docker-compose.yml**: Django app service + PostgreSQL; env and volumes for DB persistence.
- **docker-compose-debug.yml**: Same stack with volume mounts for live code, `runserver` or shell, and optional debug port.

**Commands**

| Goal              | Command |
|-------------------|--------|
| Build and run     | `docker compose up --build` |
| Run in background | `docker compose up -d` |
| Run migrations    | `docker compose run --rm app python manage.py migrate` |
| Run tests         | `docker compose run --rm app python manage.py test` |
| Debug/development | `docker compose -f docker-compose-debug.yml up --build` |
| Shell             | `docker compose run --rm app python manage.py shell` |

---

## CODEOWNERS

See [CODEOWNERS](CODEOWNERS) for code ownership and review expectations. Branch protection should require reviews from code owners where applicable.

---

## Cursor – Django Expert Skill

The project includes a **Django expert** Agent skill for backend guidance (models, ORM, views, DRF, security, performance) in `.agents/skills/django-expert/`.

**Shortcuts (Agent chat):**

- **`/django-expert`** – Run the Django expert workflow explicitly.
- **`@django-expert`** – Attach the skill as context (type `@` then the skill name).

When editing Django files, the rule in `.cursor/rules/django-conventions.mdc` is applied; use the skill above for full behavior.
