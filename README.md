# time-tracking

## Cursor – Django Expert Skill

The project includes a **Django expert** Agent skill for backend guidance (models, ORM, views, DRF, security, performance). The skill lives in `.agents/skills/django-expert/` and is also exposed under `.cursor/skills/django-expert` (symlink).

**Shortcuts (Agent chat):**

- **`/django-expert`** – Run the Django expert workflow explicitly.
- **`@django-expert`** – Attach the skill as context to your message (type `@` then the skill name).

When editing Django files (`models.py`, `views.py`, `serializers.py`, `urls.py`, `admin.py`), the rule in `.cursor/rules/django-conventions.mdc` is applied for conventions; use the skill above for full behavior.