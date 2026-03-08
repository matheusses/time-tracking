"""
Integration tests: auth/permissions (authenticated vs anonymous, user sees only own data).
Transaction boundaries where relevant.
"""
from datetime import date, datetime

from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from core.tests.factories import (
    project_factory,
    task_type_factory,
    time_entry_factory,
    user_factory,
)


class TimerAuthIntegrationTests(TestCase):
    """Timer endpoints: authenticated vs anonymous."""

    def setUp(self):
        self.client = Client()

    def test_timer_partial_anonymous_redirects_to_login(self):
        response = self.client.get(reverse("tracking:timer_partial"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response.url)

    def test_timer_start_post_anonymous_redirects_to_login(self):
        response = self.client.post(reverse("tracking:timer_start"), {})
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response.url)

    def test_timer_stop_post_anonymous_redirects_to_login(self):
        response = self.client.post(reverse("tracking:timer_stop"), {})
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response.url)

    def test_timer_partial_authenticated_returns_200(self):
        user = user_factory()
        self.client.force_login(user)
        response = self.client.get(reverse("tracking:timer_partial"))
        self.assertEqual(response.status_code, 200)


class TimesheetAuthIntegrationTests(TestCase):
    """Timesheet endpoints: authenticated vs anonymous."""

    def setUp(self):
        self.client = Client()

    def test_timesheet_page_anonymous_redirects_to_login(self):
        response = self.client.get(reverse("tracking:timesheet"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response.url)

    def test_timesheet_grid_anonymous_redirects_to_login(self):
        response = self.client.get(
            reverse("tracking:timesheet_grid"), {"week": "2025-W10"}
        )
        self.assertEqual(response.status_code, 302)

    def test_timesheet_update_post_anonymous_redirects_to_login(self):
        response = self.client.post(reverse("tracking:timesheet_update"), {})
        self.assertEqual(response.status_code, 302)


class UserDataIsolationIntegrationTests(TestCase):
    """User can only see own data (timesheet and timer)."""

    def setUp(self):
        self.user_a = user_factory()
        self.user_b = user_factory()
        self.client = Client()

    def test_timesheet_returns_only_own_entries(self):
        """Generate weekly timesheet for user_a; entries for user_b must not appear."""
        project = project_factory()
        task = task_type_factory()
        tz = timezone.get_current_timezone()
        week_start = date(2025, 3, 3)
        time_entry_factory(
            user=self.user_b,
            project=project,
            task_type=task,
            started_at=timezone.make_aware(datetime(2025, 3, 3, 10, 0), tz),
            ended_at=timezone.make_aware(datetime(2025, 3, 3, 11, 0), tz),
        )
        self.client.force_login(self.user_a)
        response = self.client.get(
            reverse("tracking:timesheet_grid"), {"week": "2025-W10"}
        )
        self.assertEqual(response.status_code, 200)
        # Grid for user_a should have no rows (user_a has no entries; user_b's entries not visible)
        from core.di import get_track_client
        track = get_track_client()
        dto = track.generate_weekly_timesheet(
            self.user_a.id, week_start, include_empty_rows=False
        )
        self.assertEqual(len(dto.rows), 0)

    def test_timer_start_creates_entry_for_logged_in_user_only(self):
        self.client.force_login(self.user_a)
        self.client.post(reverse("tracking:timer_start"), {})
        from tracking.models import TimeEntry
        self.assertEqual(
            TimeEntry.objects.filter(user=self.user_a, ended_at__isnull=True).count(), 1
        )
        self.assertEqual(
            TimeEntry.objects.filter(user=self.user_b, ended_at__isnull=True).count(), 0
        )
