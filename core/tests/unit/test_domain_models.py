"""
Unit tests for domain models: invariants and validation (e.g. hours >= 0, date in range).
"""
import dataclasses
from datetime import datetime, timezone

from django.test import TestCase

from tracking.domain.models import ActiveTimerState, TimerResult


class ActiveTimerStateTests(TestCase):
    """Test ActiveTimerState: invariants and duration_seconds property."""

    def test_duration_seconds_is_none_while_running(self):
        """Invariant: active timer has no end time, so duration_seconds is None."""
        state = ActiveTimerState(
            entry_id=1,
            project_id=None,
            project_name=None,
            task_type_id=None,
            task_type_name=None,
            started_at=datetime.now(timezone.utc),
        )
        self.assertIsNone(state.duration_seconds)

    def test_frozen_immutable(self):
        state = ActiveTimerState(
            entry_id=1,
            project_id=2,
            project_name="P",
            task_type_id=3,
            task_type_name="T",
            started_at=datetime.now(timezone.utc),
        )
        with self.assertRaises(dataclasses.FrozenInstanceError):
            state.entry_id = 99  # type: ignore[misc]


class TimerResultTests(TestCase):
    """Test TimerResult: success, message, optional stopped info."""

    def test_success_result_has_active_timer(self):
        active = ActiveTimerState(
            entry_id=1,
            project_id=None,
            project_name=None,
            task_type_id=None,
            task_type_name=None,
            started_at=datetime.now(timezone.utc),
        )
        result = TimerResult(
            success=True,
            message="Started.",
            active_timer=active,
        )
        self.assertTrue(result.success)
        self.assertIsNotNone(result.active_timer)
        self.assertIsNone(result.stopped_entry_id)
        self.assertIsNone(result.stopped_duration_seconds)

    def test_stop_result_has_stopped_entry_id_and_duration(self):
        result = TimerResult(
            success=True,
            message="Stopped.",
            active_timer=None,
            stopped_entry_id=42,
            stopped_duration_seconds=3600,
        )
        self.assertTrue(result.success)
        self.assertEqual(result.stopped_entry_id, 42)
        self.assertEqual(result.stopped_duration_seconds, 3600)

    def test_failure_result_no_active_timer(self):
        result = TimerResult(
            success=False,
            message="No active timer to stop.",
            active_timer=None,
        )
        self.assertFalse(result.success)
        self.assertIsNone(result.active_timer)
