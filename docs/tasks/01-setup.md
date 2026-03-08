# Setup — Implementation Task Summary

## Relevant Files

### Core Implementation Files

- `project/settings.py` - Django 5.2+/6.0+ config, PostgreSQL DATABASES, INSTALLED_APPS, base settings
- `project/urls.py` - Root URL configuration
- `templates/base.html` - Base template with HTMX script and Tailwind CSS (CDN or build)
- App layout: presentation (views, templates), application (use_cases, DTOs), domain (services, models), infrastructure (ORM usage inside services only)

### Integration Points

- `requirements.txt` or `pyproject.toml` - Python dependencies (Django 5.2+, psycopg, etc.)
- Environment/config for database URL and secrets (e.g. `.env`, 12-factor)

### Container / Docker

- `Dockerfile` - Multi-stage image: builder stage (install deps, optional static/tooling), final stage (slim runtime, copy app and deps, non-root user, run server)
- `docker-compose.yml` (or `compose.yaml`) - Compose stack: Django app service + PostgreSQL service, env, volumes for DB persistence
- `docker-compose-debug.yml` - Debug/development Compose: same services with volume mounts for live code, debugger port, runserver or shell, optional debug tools
- `.dockerignore` - Exclude git, `__pycache__`, `.env`, virtualenvs, and other non-build artifacts

### Documentation Files

- `README.md` - Setup, run, test commands; security considerations
- `docs/adr/architectural_decision.md` - ADR reference for layered architecture
- `CODEOWNERS` - Code ownership and review expectations

## Tasks

- [x] 1.0 Create Django project and app structure (Django 5.2+ or 6.0+)
- [x] 2.0 Configure PostgreSQL database and connection
- [x] 3.0 Add HTMX and Tailwind CSS (CDN or build; align with django-htmx-tailwind skill)
- [x] 4.0 Establish folder structure reflecting ADR layers (e.g. `use_cases/`, `domain/services/`, `domain/models/`, views/templates)
- [x] 5.0 Document setup, run, and test commands (local and Docker) in README; security considerations and CODEOWNERS
- [x] 6.0 Add multi-stage Dockerfile and Docker Compose: app service + PostgreSQL, env/config for DB and secrets. Add `docker-compose-debug.yml` for debug/development (volume mounts, debug port, runserver/shell). Document Docker and debug-compose commands in README
