"""Unit tests for project_management client (list clients, projects, task types via DI)."""
from django.test import TestCase

from core.di import get_project_management_client
from project_management.application.dtos import ClientOptionDTO, ProjectOptionDTO, TaskTypeOptionDTO
from project_management.tests.factories import (
    ClientFactory,
    ProjectFactory,
    TaskTypeFactory,
    UserFactory,
    UserProfileFactory,
)


class ListClientsClientTests(TestCase):
    def setUp(self):
        self.pm_client = get_project_management_client()

    def test_staff_gets_all_clients(self):
        ClientFactory(name="A")
        ClientFactory(name="B")
        user = UserFactory(is_staff=True)
        result = self.pm_client.list_clients(user_id=user.id, is_staff=True)
        self.assertEqual(len(result), 2)
        self.assertIsInstance(result[0], ClientOptionDTO)
        self.assertIn(result[0].name, ("A", "B"))

    def test_non_staff_with_profile_gets_only_their_client(self):
        c = ClientFactory(name="Only")
        user = UserFactory(is_staff=False)
        UserProfileFactory(user=user, client=c)
        result = self.pm_client.list_clients(user_id=user.id, is_staff=False)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].name, "Only")


class ListProjectsClientTests(TestCase):
    def setUp(self):
        self.pm_client = get_project_management_client()

    def test_staff_gets_all_projects(self):
        client = ClientFactory()
        ProjectFactory(client=client, name="P1")
        user = UserFactory(is_staff=True)
        result = self.pm_client.list_projects(user_id=user.id, is_staff=True)
        self.assertEqual(len(result), 1)
        self.assertIsInstance(result[0], ProjectOptionDTO)
        self.assertEqual(result[0].name, "P1")
        self.assertEqual(result[0].client_id, client.id)

    def test_non_staff_gets_only_their_client_projects(self):
        client = ClientFactory()
        ProjectFactory(client=client, name="P1")
        user = UserFactory(is_staff=False)
        UserProfileFactory(user=user, client=client)
        result = self.pm_client.list_projects(user_id=user.id, is_staff=False)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].name, "P1")


class ListTaskTypesClientTests(TestCase):
    def setUp(self):
        self.pm_client = get_project_management_client()

    def test_returns_all_task_types(self):
        TaskTypeFactory(name="Dev")
        TaskTypeFactory(name="Meeting")
        result = self.pm_client.list_task_types()
        self.assertEqual(len(result), 2)
        self.assertIsInstance(result[0], TaskTypeOptionDTO)
        names = [t.name for t in result]
        self.assertIn("Dev", names)
        self.assertIn("Meeting", names)


class GetTimerOptionsClientTests(TestCase):
    def setUp(self):
        self.pm_client = get_project_management_client()

    def test_returns_projects_and_task_types(self):
        client = ClientFactory()
        ProjectFactory(client=client, name="P1")
        TaskTypeFactory(name="T1")
        user = UserFactory(is_staff=True)
        result = self.pm_client.get_timer_options(user_id=user.id, is_staff=True)
        self.assertEqual(len(result.projects), 1)
        self.assertEqual(result.projects[0].name, "P1")
        self.assertEqual(len(result.task_types), 1)
        self.assertEqual(result.task_types[0].name, "T1")
