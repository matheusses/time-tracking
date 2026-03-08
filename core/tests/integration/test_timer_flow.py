"""
Integration tests: timer flow with real DB (start → stop → assert entry and duration).
"""
from datetime import timedelta
from unittest.mock import patch

from django.test import TestCase
from django.utils import timezone

from core.di import get_track_client
from core.tests.factories import (
    project_factory,
    task_type_factory,
    user_factory,
)
from tracking.application.dtos import StartTimerInputDTO, StopTimerInputDTO
from tracking.models import TimeEntry


class TimerFlowIntegrationTests(TestCase):
    """End-to-end timer flow with real database: start, stop, assert entry and duration."""

    def setUp(self):
        self.user = user_factory()
        self.client = get_track_client()

    def test_start_then_stop_creates_completed_entry_with_duration(self):
        self.client.start_timer(StartTimerInputDTO(user_id=self.user.id))
        entry_before = TimeEntry.objects.get(user=self.user, ended_at__isnull=True)
        start = entry_before.started_at
        end = start + timedelta(seconds=3723)  # 1h 2m 3s
        with patch(
            "tracking.domain.services.timer_service.django_tz.now", return_value=end
        ):
            result = self.client.stop_timer(StopTimerInputDTO(user_id=self.user.id))
        self.assertTrue(result.success)
        self.assertEqual(result.stopped_duration_seconds, 3723)
        self.assertIsNone(result.active_timer)
        entry = TimeEntry.objects.get(pk=entry_before.id)
        self.assertIsNotNone(entry.ended_at)
        self.assertEqual(
            int((entry.ended_at - entry.started_at).total_seconds()), 3723
        )

    def test_start_with_project_and_task_then_stop_persists_relations(self):
        project = project_factory(name="Integration Project")
        task_type = task_type_factory(name="Development")
        self.client.start_timer(
            StartTimerInputDTO(
                user_id=self.user.id,
                project_id=project.id,
                task_type_id=task_type.id,
            )
        )
        result = self.client.stop_timer(StopTimerInputDTO(user_id=self.user.id))
        self.assertTrue(result.success)
        entry = TimeEntry.objects.filter(user=self.user).order_by("-id").first()
        self.assertEqual(entry.project_id, project.id)
        self.assertEqual(entry.task_type_id, task_type.id)

    def test_multiple_start_stop_cycles_each_produces_one_completed_entry(self):
        for _ in range(3):
            self.client.start_timer(StartTimerInputDTO(user_id=self.user.id))
            self.client.stop_timer(StopTimerInputDTO(user_id=self.user.id))
        self.assertEqual(
            TimeEntry.objects.filter(user=self.user, ended_at__isnull=False).count(), 3
        )
        self.assertEqual(
            TimeEntry.objects.filter(user=self.user, ended_at__isnull=True).count(), 0
        )
