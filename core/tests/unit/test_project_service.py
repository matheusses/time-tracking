"""
Unit tests for ProjectService: list clients, list projects by client, list task types.
"""
from django.test import TestCase

from core.tests.factories import (
    client_factory,
    project_factory,
    task_type_factory,
    user_factory,
    user_profile_factory,
)
from project_management.domain.services.project_service import ProjectService


class ProjectServiceListClientsTests(TestCase):
    """Test list_clients_for_user: staff sees all, non-staff sees only their client."""

    def setUp(self):
        self.service = ProjectService()
        self.client_a = client_factory(name="Client A")
        self.client_b = client_factory(name="Client B")

    def test_staff_sees_all_clients(self):
        user = user_factory(is_staff=True)
        rows = self.service.list_clients_for_user(user.id, is_staff=True)
        self.assertEqual(len(rows), 2)
        names = [r[1] for r in rows]
        self.assertIn("Client A", names)
        self.assertIn("Client B", names)

    def test_non_staff_without_profile_sees_none(self):
        user = user_factory(is_staff=False)
        rows = self.service.list_clients_for_user(user.id, is_staff=False)
        self.assertEqual(len(rows), 0)

    def test_non_staff_with_profile_sees_only_their_client(self):
        user = user_factory(is_staff=False)
        user_profile_factory(user=user, client=self.client_a)
        rows = self.service.list_clients_for_user(user.id, is_staff=False)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0][1], "Client A")


class ProjectServiceListProjectsTests(TestCase):
    """Test list_projects_for_user: hierarchy and filtering by client."""

    def setUp(self):
        self.service = ProjectService()
        self.client_a = client_factory(name="Client A")
        self.client_b = client_factory(name="Client B")
        self.project_a1 = project_factory(client=self.client_a, name="Proj A1")
        self.project_a2 = project_factory(client=self.client_a, name="Proj A2")
        self.project_b1 = project_factory(client=self.client_b, name="Proj B1")

    def test_staff_sees_all_projects(self):
        user = user_factory(is_staff=True)
        rows = self.service.list_projects_for_user(user.id, is_staff=True)
        self.assertEqual(len(rows), 3)

    def test_staff_with_client_id_filter_sees_only_that_client_projects(self):
        user = user_factory(is_staff=True)
        rows = self.service.list_projects_for_user(
            user.id, is_staff=True, client_id=self.client_a.id
        )
        self.assertEqual(len(rows), 2)
        names = [r[1] for r in rows]
        self.assertIn("Proj A1", names)
        self.assertIn("Proj A2", names)
        self.assertNotIn("Proj B1", names)

    def test_non_staff_sees_only_their_client_projects(self):
        user = user_factory(is_staff=False)
        user_profile_factory(user=user, client=self.client_a)
        rows = self.service.list_projects_for_user(user.id, is_staff=False)
        self.assertEqual(len(rows), 2)
        names = [r[1] for r in rows]
        self.assertIn("Proj A1", names)
        self.assertIn("Proj A2", names)
        self.assertNotIn("Proj B1", names)

    def test_non_staff_without_profile_sees_none(self):
        user = user_factory(is_staff=False)
        rows = self.service.list_projects_for_user(user.id, is_staff=False)
        self.assertEqual(len(rows), 0)


class ProjectServiceListTaskTypesTests(TestCase):
    """Test list_task_types: global list."""

    def setUp(self):
        self.service = ProjectService()
        task_type_factory(name="Development")
        task_type_factory(name="Meeting")

    def test_returns_all_task_types(self):
        rows = self.service.list_task_types()
        self.assertEqual(len(rows), 2)
        names = [r[1] for r in rows]
        self.assertIn("Development", names)
        self.assertIn("Meeting", names)


class ProjectServiceGetUserClientIdTests(TestCase):
    """Test get_user_client_id."""

    def setUp(self):
        self.service = ProjectService()

    def test_returns_none_when_no_profile(self):
        user = user_factory()
        self.assertIsNone(self.service.get_user_client_id(user.id))

    def test_returns_client_id_when_profile_exists(self):
        user = user_factory()
        client = client_factory()
        user_profile_factory(user=user, client=client)
        self.assertEqual(self.service.get_user_client_id(user.id), client.id)
