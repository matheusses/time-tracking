"""
Unit tests for TimerService: single active timer per user, start/stop behavior.
"""
from datetime import timedelta
from unittest.mock import patch

from django.test import TestCase
from django.utils import timezone

from tracking.domain.services.timer_service import TimerService
from tracking.models import TimeEntry
from tracking.tests.factories import ProjectFactory, TaskTypeFactory, UserFactory


class TimerServiceStartTests(TestCase):
    """Test TimerService.start(): single active timer, stop-before-start."""

    def setUp(self):
        self.service = TimerService()
        self.user = UserFactory()

    def test_start_creates_active_entry(self):
        result = self.service.start(self.user.id)
        self.assertTrue(result.success)
        self.assertIsNotNone(result.active_timer)
        self.assertEqual(TimeEntry.objects.filter(user=self.user, ended_at__isnull=True).count(), 1)

    def test_start_stops_existing_active_timer(self):
        self.service.start(self.user.id)
        self.service.start(self.user.id)
        active_count = TimeEntry.objects.filter(user=self.user, ended_at__isnull=True).count()
        self.assertEqual(active_count, 1)
        completed = TimeEntry.objects.filter(user=self.user, ended_at__isnull=False)
        self.assertEqual(completed.count(), 1)

    def test_start_with_optional_project_and_task_type(self):
        project = ProjectFactory(name="Test Project")
        task_type = TaskTypeFactory(name="Development")
        result = self.service.start(
            self.user.id,
            project_id=project.id,
            task_type_id=task_type.id,
        )
        self.assertTrue(result.success)
        entry = TimeEntry.objects.get(user=self.user, ended_at__isnull=True)
        self.assertEqual(entry.project_id, project.id)
        self.assertEqual(entry.task_type_id, task_type.id)

    def test_start_without_project_or_task_type(self):
        result = self.service.start(self.user.id)
        self.assertTrue(result.success)
        entry = TimeEntry.objects.get(user=self.user, ended_at__isnull=True)
        self.assertIsNone(entry.project_id)
        self.assertIsNone(entry.task_type_id)


class TimerServiceStopTests(TestCase):
    """Test TimerService.stop(): only active timer stopped, duration computed."""

    def setUp(self):
        self.service = TimerService()
        self.user = UserFactory()

    def test_stop_with_no_active_timer_returns_failure(self):
        result = self.service.stop(self.user.id)
        self.assertFalse(result.success)
        self.assertIn("No active timer", result.message)

    def test_stop_sets_ended_at_and_returns_duration(self):
        self.service.start(self.user.id)
        entry = TimeEntry.objects.get(user=self.user, ended_at__isnull=True)
        start = entry.started_at
        end = start + timedelta(seconds=3600)
        with patch("tracking.domain.services.timer_service.django_tz.now", return_value=end):
            result = self.service.stop(self.user.id)
        self.assertTrue(result.success)
        self.assertEqual(result.stopped_duration_seconds, 3600)
        entry.refresh_from_db()
        self.assertIsNotNone(entry.ended_at)

    def test_get_active_timer_returns_none_when_none(self):
        self.assertIsNone(self.service.get_active_timer(self.user.id))

    def test_get_active_timer_returns_state_when_running(self):
        self.service.start(self.user.id)
        active = self.service.get_active_timer(self.user.id)
        self.assertIsNotNone(active)
        self.assertIsNotNone(active.entry_id)
        self.assertEqual(active.started_at, TimeEntry.objects.get(user=self.user).started_at)

    def test_get_active_timer_includes_project_and_task_type_names_when_set(self):
        """Active timer state exposes project_name and task_type_name from related models."""
        project = ProjectFactory(name="My Project")
        task_type = TaskTypeFactory(name="Development")
        self.service.start(
            self.user.id,
            project_id=project.id,
            task_type_id=task_type.id,
        )
        active = self.service.get_active_timer(self.user.id)
        self.assertIsNotNone(active)
        self.assertEqual(active.project_id, project.id)
        self.assertEqual(active.project_name, "My Project")
        self.assertEqual(active.task_type_id, task_type.id)
        self.assertEqual(active.task_type_name, "Development")

    def test_single_active_timer_per_user_only_one_running_at_a_time(self):
        """Enforce single-timer rule: after start, exactly one entry has ended_at=None."""
        self.service.start(self.user.id)
        self.service.start(self.user.id)
        self.service.start(self.user.id)
        active_count = TimeEntry.objects.filter(user=self.user, ended_at__isnull=True).count()
        self.assertEqual(active_count, 1)
        completed_count = TimeEntry.objects.filter(user=self.user, ended_at__isnull=False).count()
        self.assertEqual(completed_count, 2)
