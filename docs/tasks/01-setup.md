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

### Documentation Files

- `README.md` - Setup, run, test commands; security considerations
- `docs/adr/architectural_decision.md` - ADR reference for layered architecture
- `CODEOWNERS` - Code ownership and review expectations

## Tasks

- [ ] 1.0 Create Django project and app structure (Django 5.2+ or 6.0+)
- [ ] 2.0 Configure PostgreSQL database and connection
- [ ] 3.0 Add HTMX and Tailwind CSS (CDN or build; align with django-htmx-tailwind skill)
- [ ] 4.0 Establish folder structure reflecting ADR layers (e.g. `use_cases/`, `domain/services/`, `domain/models/`, views/templates)
- [ ] 5.0 Document setup, run, and test commands in README; security considerations and CODEOWNERS
