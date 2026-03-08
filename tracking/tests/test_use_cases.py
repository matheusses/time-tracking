"""Unit tests for timer use cases."""
from django.test import TestCase

from tracking.application.dtos import StartTimerInputDTO, StopTimerInputDTO
from tracking.models import TimeEntry
from tracking.use_cases.start_timer import execute as start_timer
from tracking.use_cases.stop_timer import execute as stop_timer
from tracking.tests.factories import UserFactory


class StartTimerUseCaseTests(TestCase):
    def setUp(self):
        self.user = UserFactory()

    def test_execute_starts_timer(self):
        dto = StartTimerInputDTO(user_id=self.user.id)
        result = start_timer(dto)
        self.assertTrue(result.success)
        self.assertEqual(TimeEntry.objects.filter(user=self.user, ended_at__isnull=True).count(), 1)

    def test_execute_with_project_and_task_type(self):
        from tracking.tests.factories import ProjectFactory, TaskTypeFactory
        project = ProjectFactory(name="P")
        task_type = TaskTypeFactory(name="T")
        dto = StartTimerInputDTO(user_id=self.user.id, project_id=project.id, task_type_id=task_type.id)
        result = start_timer(dto)
        self.assertTrue(result.success)
        entry = TimeEntry.objects.get(user=self.user, ended_at__isnull=True)
        self.assertEqual(entry.project_id, project.id)
        self.assertEqual(entry.task_type_id, task_type.id)


class StopTimerUseCaseTests(TestCase):
    def setUp(self):
        self.user = UserFactory()

    def test_execute_stops_active_timer(self):
        start_timer(StartTimerInputDTO(user_id=self.user.id))
        dto = StopTimerInputDTO(user_id=self.user.id)
        result = stop_timer(dto)
        self.assertTrue(result.success)
        self.assertIsNone(result.active_timer)
        self.assertEqual(TimeEntry.objects.filter(user=self.user, ended_at__isnull=True).count(), 0)

    def test_execute_with_no_active_timer_fails_gracefully(self):
        dto = StopTimerInputDTO(user_id=self.user.id)
        result = stop_timer(dto)
        self.assertFalse(result.success)
