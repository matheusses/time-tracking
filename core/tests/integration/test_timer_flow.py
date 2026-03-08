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
from tracking.models import TimeEntry, TimerAction


class TimerFlowIntegrationTests(TestCase):
    """End-to-end timer flow with real database: start, stop, assert entry and duration. project_id and task_type_id required for start."""

    def setUp(self):
        self.user = user_factory()
        self.client = get_track_client()
        self.project = project_factory(name="Flow Project")
        self.task_type = task_type_factory(name="Dev")

    def _start_dto(self):
        return StartTimerInputDTO(
            user_id=self.user.id,
            project_id=self.project.id,
            task_type_id=self.task_type.id,
        )

    def test_start_then_stop_creates_completed_entry_with_duration(self):
        self.client.start_timer(self._start_dto())
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
        self.client.start_timer(self._start_dto())
        result = self.client.stop_timer(StopTimerInputDTO(user_id=self.user.id))
        self.assertTrue(result.success)
        entry = TimeEntry.objects.filter(user=self.user).order_by("-id").first()
        self.assertEqual(entry.project_id, self.project.id)
        self.assertEqual(entry.task_type_id, self.task_type.id)

    def test_multiple_start_stop_cycles_each_produces_one_completed_entry(self):
        for _ in range(3):
            self.client.start_timer(self._start_dto())
            self.client.stop_timer(StopTimerInputDTO(user_id=self.user.id))
        self.assertEqual(
            TimeEntry.objects.filter(user=self.user, ended_at__isnull=False).count(), 3
        )
        self.assertEqual(
            TimeEntry.objects.filter(user=self.user, ended_at__isnull=True).count(), 0
        )

    def test_timer_actions_have_time_entry_id_set(self):
        """TimerAction rows (event log) must have time_entry_id linking to the TimeEntry."""
        self.client.start_timer(self._start_dto())
        entry = TimeEntry.objects.get(user=self.user, ended_at__isnull=True)
        start_actions = TimerAction.objects.filter(
            user=self.user, action=TimerAction.Action.START
        )
        self.assertEqual(start_actions.count(), 1)
        self.assertEqual(start_actions.get().time_entry_id, entry.id)
        self.client.stop_timer(StopTimerInputDTO(user_id=self.user.id))
        stop_actions = TimerAction.objects.filter(
            user=self.user, action=TimerAction.Action.STOP
        )
        self.assertEqual(stop_actions.count(), 1)
        self.assertEqual(stop_actions.get().time_entry_id, entry.id)
