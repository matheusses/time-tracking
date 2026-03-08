"""Unit tests for DI container: clients resolve and expose expected methods."""
from datetime import date

from django.test import TestCase

from core.di import get_project_management_client, get_track_client
from tracking.application.dtos import StartTimerInputDTO, StopTimerInputDTO
from tracking.tests.factories import UserFactory


class DITests(TestCase):
    """Verify DI container resolves clients that implement the expected interface."""

    def test_get_track_client_returns_client_with_expected_methods(self):
        client = get_track_client()
        self.assertTrue(hasattr(client, "generate_weekly_timesheet"))
        self.assertTrue(hasattr(client, "get_active_timer"))
        self.assertTrue(hasattr(client, "start_timer"))
        self.assertTrue(hasattr(client, "stop_timer"))
        self.assertTrue(hasattr(client, "update_time_entry"))
        self.assertTrue(hasattr(client, "has_entries_in_week"))

    def test_get_project_management_client_returns_client_with_expected_methods(self):
        client = get_project_management_client()
        self.assertTrue(hasattr(client, "get_timer_options"))
        self.assertTrue(hasattr(client, "list_projects"))
        self.assertTrue(hasattr(client, "list_clients"))
        self.assertTrue(hasattr(client, "list_task_types"))

    def test_track_client_get_active_timer_returns_none_when_no_timer(self):
        user = UserFactory()
        client = get_track_client()
        self.assertIsNone(client.get_active_timer(user.id))

    def test_track_client_has_entries_in_week_returns_false_when_no_entries(self):
        user = UserFactory()
        client = get_track_client()
        week_start = date(2025, 3, 3)  # Monday
        self.assertFalse(client.has_entries_in_week(user.id, week_start))

    def test_track_client_start_and_stop_flow(self):
        user = UserFactory()
        client = get_track_client()
        result = client.start_timer(StartTimerInputDTO(user_id=user.id))
        self.assertTrue(result.success)
        self.assertIsNotNone(result.active_timer)
        result2 = client.stop_timer(StopTimerInputDTO(user_id=user.id))
        self.assertTrue(result2.success)
        self.assertIsNone(result2.active_timer)
