"""Test factories for project_management (Client, Project, TaskType, UserProfile)."""
from django.contrib.auth import get_user_model

from project_management.models import Client, Project, TaskType, UserProfile

User = get_user_model()


def UserFactory(**kwargs):
    """Create a user for tests."""
    defaults = {"username": f"user_{id(object)}", "email": f"user_{id(object)}@example.com"}
    if "password" not in kwargs:
        kwargs["password"] = "testpass123!"
    return User.objects.create_user(**(defaults | kwargs))


def ClientFactory(**kwargs):
    """Create a client for tests."""
    defaults = {"name": f"Client {id(object)}"}
    return Client.objects.create(**(defaults | kwargs))


def ProjectFactory(client=None, **kwargs):
    """Create a project for tests."""
    if client is None:
        client = ClientFactory()
    defaults = {"name": f"Project {id(object)}", "client": client}
    return Project.objects.create(**(defaults | kwargs))


def TaskTypeFactory(**kwargs):
    """Create a task type for tests."""
    defaults = {"name": f"TaskType {id(object)}"}
    return TaskType.objects.create(**(defaults | kwargs))


def UserProfileFactory(user=None, client=None, **kwargs):
    """Create a user profile (user–client association) for tests."""
    if user is None:
        user = UserFactory()
    if client is None:
        client = ClientFactory()
    return UserProfile.objects.create(user=user, client=client, **kwargs)
