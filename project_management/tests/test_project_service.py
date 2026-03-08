"""Unit tests for ProjectService: list clients/projects/task types scoped by user."""
from django.test import TestCase

from project_management.domain.services.project_service import ProjectService
from project_management.tests.factories import (
    ClientFactory,
    ProjectFactory,
    TaskTypeFactory,
    UserFactory,
    UserProfileFactory,
)


class ProjectServiceListClientsTests(TestCase):
    """Test list_clients_for_user scoping: staff sees all, non-staff sees only their client."""

    def setUp(self):
        self.service = ProjectService()
        self.client_a = ClientFactory(name="Client A")
        self.client_b = ClientFactory(name="Client B")

    def test_staff_sees_all_clients(self):
        user = UserFactory(is_staff=True)
        clients = self.service.list_clients_for_user(user.id, is_staff=True)
        self.assertEqual(len(clients), 2)
        names = [c.name for c in clients]
        self.assertIn("Client A", names)
        self.assertIn("Client B", names)

    def test_non_staff_without_profile_sees_none(self):
        user = UserFactory(is_staff=False)
        clients = self.service.list_clients_for_user(user.id, is_staff=False)
        self.assertEqual(len(clients), 0)

    def test_non_staff_with_profile_sees_only_their_client(self):
        user = UserFactory(is_staff=False)
        UserProfileFactory(user=user, client=self.client_a)
        clients = self.service.list_clients_for_user(user.id, is_staff=False)
        self.assertEqual(len(clients), 1)
        self.assertEqual(clients[0].name, "Client A")


class ProjectServiceListProjectsTests(TestCase):
    """Test list_projects_for_user scoping by user's client."""

    def setUp(self):
        self.service = ProjectService()
        self.client_a = ClientFactory(name="Client A")
        self.client_b = ClientFactory(name="Client B")
        self.project_a1 = ProjectFactory(client=self.client_a, name="Proj A1")
        self.project_a2 = ProjectFactory(client=self.client_a, name="Proj A2")
        self.project_b1 = ProjectFactory(client=self.client_b, name="Proj B1")

    def test_staff_sees_all_projects(self):
        user = UserFactory(is_staff=True)
        projects = self.service.list_projects_for_user(user.id, is_staff=True)
        self.assertEqual(len(projects), 3)

    def test_non_staff_sees_only_their_client_projects(self):
        user = UserFactory(is_staff=False)
        UserProfileFactory(user=user, client=self.client_a)
        projects = self.service.list_projects_for_user(user.id, is_staff=False)
        self.assertEqual(len(projects), 2)
        names = [p.name for p in projects]
        self.assertIn("Proj A1", names)
        self.assertIn("Proj A2", names)
        self.assertNotIn("Proj B1", names)

    def test_non_staff_without_profile_sees_none(self):
        user = UserFactory(is_staff=False)
        projects = self.service.list_projects_for_user(user.id, is_staff=False)
        self.assertEqual(len(projects), 0)


class ProjectServiceListTaskTypesTests(TestCase):
    """Test list_task_types (global list)."""

    def setUp(self):
        self.service = ProjectService()
        TaskTypeFactory(name="Development")
        TaskTypeFactory(name="Meeting")

    def test_returns_all_task_types(self):
        task_types = self.service.list_task_types()
        self.assertEqual(len(task_types), 2)
        names = [t.name for t in task_types]
        self.assertIn("Development", names)
        self.assertIn("Meeting", names)
