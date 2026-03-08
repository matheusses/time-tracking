"""
Shared test factories for core test suite.
Re-exports and wraps tracking and project_management factories for a single import point.
"""
from django.contrib.auth import get_user_model
from project_management.models import Client, Project, TaskType, UserProfile
from tracking.models import TimeEntry

User = get_user_model()


def user_factory(**kwargs):
    """Create a user. Uses unique username/email per call."""
    import uuid
    uid = uuid.uuid4().hex[:8]
    defaults = {"username": f"user_{uid}", "email": f"user_{uid}@example.com"}
    if "password" not in kwargs:
        kwargs["password"] = "testpass123!"
    return User.objects.create_user(**(defaults | kwargs))


def client_factory(**kwargs):
    """Create a client."""
    defaults = {"name": f"Client {id(object)}"}
    return Client.objects.create(**(defaults | kwargs))


def project_factory(client=None, **kwargs):
    """Create a project (client created if not provided)."""
    if client is None:
        client = client_factory()
    defaults = {"name": f"Project {id(object)}", "client": client}
    return Project.objects.create(**(defaults | kwargs))


def task_type_factory(**kwargs):
    """Create a task type."""
    defaults = {"name": f"TaskType {id(object)}"}
    return TaskType.objects.create(**(defaults | kwargs))


def user_profile_factory(user=None, client=None, **kwargs):
    """Create a user profile (user–client association)."""
    if user is None:
        user = user_factory()
    if client is None:
        client = client_factory()
    return UserProfile.objects.create(user=user, client=client, **kwargs)


def time_entry_factory(
    user,
    started_at=None,
    ended_at=None,
    project=None,
    task_type=None,
    manual_duration_seconds=None,
    **kwargs,
):
    """Create a time entry. Defaults: started_at=now, ended_at=now+1h (completed)."""
    from datetime import timedelta
    from django.utils import timezone
    now = timezone.now()
    if started_at is None:
        started_at = now
    if ended_at is None and manual_duration_seconds is None:
        ended_at = started_at + timedelta(hours=1)
    defaults = {
        "user": user,
        "started_at": started_at,
        "ended_at": ended_at,
        "project": project,
        "task_type": task_type,
        "manual_duration_seconds": manual_duration_seconds,
    }
    defaults = {k: v for k, v in defaults.items() if v is not None}
    return TimeEntry.objects.create(**(defaults | kwargs))
