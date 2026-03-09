"""
Functional tests: HTMX start/stop timer (partial HTML and status), week navigation, inline edit.
"""
from datetime import date, timedelta

from django.test import Client, TestCase
from django.urls import reverse

from core.tests.factories import (
    project_factory,
    task_type_factory,
    user_factory,
)
from tracking.views.timesheet_views import (
    _monday_of_week,
    get_week_context_for_user,
)


class HTMXTimerFunctionalTests(TestCase):
    """HTMX timer: start/stop requests, assert partial HTML and status codes."""

    def setUp(self):
        self.client = Client()
        self.user = user_factory()

    def test_start_timer_post_returns_200_and_partial_html(self):
        self.client.force_login(self.user)
        self.client.get(reverse("tracking:home"))  # get CSRF cookie
        csrf = self.client.cookies.get("csrftoken")
        project = project_factory()
        task_type = task_type_factory()
        post_data = {
            "project_id": str(project.id),
            "task_type_id": str(task_type.id),
        }
        if csrf:
            post_data["csrfmiddlewaretoken"] = csrf.value
        response = self.client.post(reverse("tracking:timer_start"), post_data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "tracking/_timer_partial.html")
        # Partial should contain timer UI (e.g. stop button or active state)
        content = response.content.decode()
        self.assertIn("timer", content.lower() or "Timer" in content)

    def test_stop_timer_post_returns_200_and_partial_html(self):
        self.client.force_login(self.user)
        self.client.get(reverse("tracking:home"))
        csrf = self.client.cookies.get("csrftoken")
        project = project_factory()
        task_type = task_type_factory()
        post_data = {
            "project_id": str(project.id),
            "task_type_id": str(task_type.id),
        }
        if csrf:
            post_data["csrfmiddlewaretoken"] = csrf.value
        # Start first
        self.client.post(reverse("tracking:timer_start"), post_data)
        response = self.client.post(reverse("tracking:timer_stop"), post_data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "tracking/_timer_partial.html")

    def test_start_timer_with_project_and_task_type_in_post(self):
        self.client.force_login(self.user)
        self.client.get(reverse("tracking:home"))
        csrf = self.client.cookies.get("csrftoken")
        project = project_factory()
        task_type = task_type_factory()
        post_data = {
            "project_id": str(project.id),
            "task_type_id": str(task_type.id),
        }
        if csrf:
            post_data["csrfmiddlewaretoken"] = csrf.value
        response = self.client.post(reverse("tracking:timer_start"), post_data)
        self.assertEqual(response.status_code, 200)


class HTMXWeekNavigationFunctionalTests(TestCase):
    """Week navigation: change week, assert grid content."""

    def setUp(self):
        self.client = Client()
        self.user = user_factory()

    def test_timesheet_grid_accepts_week_param_and_returns_200(self):
        self.client.force_login(self.user)
        response = self.client.get(
            reverse("tracking:timesheet_grid"),
            {"week": "2025-W10"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "tracking/_timesheet_grid.html")

    def test_timesheet_grid_contains_week_context(self):
        self.client.force_login(self.user)
        response = self.client.get(
            reverse("tracking:timesheet_grid"),
            {"week": "2025-W10"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("timesheet", response.context)
        self.assertIn("week_days", response.context)
        self.assertIn("week_start", response.context)

    def test_week_nav_previous_always_visible(self):
        """Previous button is always enabled so users can add/edit past weeks."""
        self.client.force_login(self.user)
        current_monday = _monday_of_week(date.today())
        year, week_num, _ = current_monday.isocalendar()
        param = f"{year}-W{week_num:02d}"
        response = self.client.get(
            reverse("tracking:timesheet_grid"),
            {"week": param},
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["prev_enabled"])
        self.assertIn("Previous", response.content.decode())

    def test_week_nav_next_disabled_for_current_week(self):
        """Next button is disabled when viewing current week (no future weeks)."""
        self.client.force_login(self.user)
        current_monday = _monday_of_week(date.today())
        year, week_num, _ = current_monday.isocalendar()
        param = f"{year}-W{week_num:02d}"
        response = self.client.get(
            reverse("tracking:timesheet_grid"),
            {"week": param},
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context["next_enabled"])
        # Next link should not appear in nav when next_enabled is False
        content = response.content.decode()
        self.assertIn("Week of", content)
        # Template only renders Next when next_enabled; no "Next →" when disabled
        self.assertNotIn("Next →", content)

    def test_week_nav_next_enabled_for_past_week(self):
        """Next button is enabled when viewing a past week (navigate up to current)."""
        self.client.force_login(self.user)
        current_monday = _monday_of_week(date.today())
        past_monday = current_monday - timedelta(days=14)
        # Test context logic directly (avoids dependency on week param parsing in GET)
        context = get_week_context_for_user(
            self.user.id, self.user.is_staff, week_start=past_monday
        )
        self.assertTrue(
            context["next_enabled"],
            "next_enabled should be True when viewing a past week",
        )
        # Also verify via HTTP: request grid with week param
        year, week_num, _ = past_monday.isocalendar()
        param = f"{year}-W{week_num:02d}"
        response = self.client.get(
            reverse("tracking:timesheet_grid"),
            {"week": param},
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("Next →", response.content.decode())


class HTMXInlineEditFunctionalTests(TestCase):
    """Inline edit: submit value, assert response and cell partial."""

    def setUp(self):
        self.client = Client()
        self.user = user_factory()

    def test_update_time_entry_post_returns_cell_partial(self):
        self.client.force_login(self.user)
        self.client.get(reverse("tracking:timesheet"))
        csrf = self.client.cookies.get("csrftoken")
        post_data = {
            "date": "2025-03-05",
            "project_id": "",
            "task_type_id": "",
            "hours": "1.5",
        }
        if csrf:
            post_data["csrfmiddlewaretoken"] = csrf.value
        response = self.client.post(reverse("tracking:timesheet_update"), post_data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "tracking/_timesheet_cell.html")

    def test_update_time_entry_post_with_valid_hours_updates_cell(self):
        self.client.force_login(self.user)
        self.client.get(reverse("tracking:timesheet"))
        csrf = self.client.cookies.get("csrftoken")
        post_data = {
            "date": "2025-03-05",
            "project_id": "",
            "task_type_id": "",
            "hours": "2",
        }
        if csrf:
            post_data["csrfmiddlewaretoken"] = csrf.value
        response = self.client.post(reverse("tracking:timesheet_update"), post_data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'name="hours"')
