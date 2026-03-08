"""
Test factories for tracking app (User, TimeEntry).
Project and TaskType come from project_management; use ClientFactory, ProjectFactory, TaskTypeFactory.
"""
from django.contrib.auth import get_user_model

from project_management.models import Client, Project, TaskType

User = get_user_model()


def UserFactory(**kwargs):
    """Create a user for tests. Default username is unique per call."""
    defaults = {"username": f"user_{id(object)}", "email": f"user_{id(object)}@example.com"}
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
