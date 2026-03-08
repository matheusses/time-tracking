"""
Test factories for tracking app (User, TimeEntry).
Project and TaskType come from project_management; use ClientFactory, ProjectFactory, TaskTypeFactory.
"""
import uuid
from datetime import datetime, timedelta

from django.contrib.auth import get_user_model
from django.utils import timezone

from project_management.models import Client, Project, TaskType
from tracking.models import TimeEntry

User = get_user_model()


def UserFactory(**kwargs):
    """Create a user for tests. Default username is unique per call."""
    uid = uuid.uuid4().hex[:8]
    defaults = {"username": f"user_{uid}", "email": f"user_{uid}@example.com"}
    if "password" not in kwargs:
        kwargs["password"] = "testpass123!"
    return User.objects.create_user(**(defaults | kwargs))


def ClientFactory(**kwargs):
    """Create a client for tests."""
    defaults = {"name": f"Client {id(object)}"}
    return Client.objects.create(**(defaults | kwargs))


def ProjectFactory(client=None, **kwargs):
    """Create a project for tests. Requires a client (or one is created)."""
    if client is None:
        client = ClientFactory()
    defaults = {"name": f"Project {id(object)}", "client": client}
    return Project.objects.create(**(defaults | kwargs))


def TaskTypeFactory(**kwargs):
    """Create a task type for tests."""
    defaults = {"name": f"TaskType {id(object)}"}
    return TaskType.objects.create(**(defaults | kwargs))


def TimeEntryFactory(
    user,
    started_at=None,
    ended_at=None,
    project=None,
    task_type=None,
    manual_duration_seconds=None,
    **kwargs,
):
    """Create a time entry for tests. Defaults: started_at=now, ended_at=now+1h (completed)."""
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
