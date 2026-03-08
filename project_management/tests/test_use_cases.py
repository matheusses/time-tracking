"""Unit tests for project_management use cases (list clients, projects, task types)."""
from django.test import TestCase

from project_management.application.dtos import ClientOptionDTO, ProjectOptionDTO, TaskTypeOptionDTO
from project_management.tests.factories import (
    ClientFactory,
    ProjectFactory,
    TaskTypeFactory,
    UserFactory,
    UserProfileFactory,
)
from project_management.use_cases.get_timer_options import execute as get_timer_options
from project_management.use_cases.list_clients import execute as list_clients
from project_management.use_cases.list_projects import execute as list_projects
from project_management.use_cases.list_task_types import execute as list_task_types


class ListClientsUseCaseTests(TestCase):
    def test_staff_gets_all_clients(self):
        ClientFactory(name="A")
        ClientFactory(name="B")
        user = UserFactory(is_staff=True)
        result = list_clients(user_id=user.id, is_staff=True)
        self.assertEqual(len(result), 2)
        self.assertIsInstance(result[0], ClientOptionDTO)
        self.assertIn(result[0].name, ("A", "B"))

    def test_non_staff_with_profile_gets_only_their_client(self):
        c = ClientFactory(name="Only")
        user = UserFactory(is_staff=False)
        UserProfileFactory(user=user, client=c)
        result = list_clients(user_id=user.id, is_staff=False)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].name, "Only")


class ListProjectsUseCaseTests(TestCase):
    def test_staff_gets_all_projects(self):
        client = ClientFactory()
        ProjectFactory(client=client, name="P1")
        user = UserFactory(is_staff=True)
        result = list_projects(user_id=user.id, is_staff=True)
        self.assertEqual(len(result), 1)
        self.assertIsInstance(result[0], ProjectOptionDTO)
        self.assertEqual(result[0].name, "P1")
        self.assertEqual(result[0].client_id, client.id)

    def test_non_staff_gets_only_their_client_projects(self):
        client = ClientFactory()
        ProjectFactory(client=client, name="P1")
        user = UserFactory(is_staff=False)
        UserProfileFactory(user=user, client=client)
        result = list_projects(user_id=user.id, is_staff=False)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].name, "P1")


class ListTaskTypesUseCaseTests(TestCase):
    def test_returns_all_task_types(self):
        TaskTypeFactory(name="Dev")
        TaskTypeFactory(name="Meeting")
        result = list_task_types()
        self.assertEqual(len(result), 2)
        self.assertIsInstance(result[0], TaskTypeOptionDTO)
        names = [t.name for t in result]
        self.assertIn("Dev", names)
        self.assertIn("Meeting", names)


class GetTimerOptionsUseCaseTests(TestCase):
    def test_returns_projects_and_task_types(self):
        client = ClientFactory()
        ProjectFactory(client=client, name="P1")
        TaskTypeFactory(name="T1")
        user = UserFactory(is_staff=True)
        result = get_timer_options(user_id=user.id, is_staff=True)
        self.assertEqual(len(result.projects), 1)
        self.assertEqual(result.projects[0].name, "P1")
        self.assertEqual(len(result.task_types), 1)
        self.assertEqual(result.task_types[0].name, "T1")
