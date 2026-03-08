"""
Functional tests: HTMX start/stop timer (partial HTML and status), week navigation, inline edit.
"""
from datetime import date

from django.test import Client, TestCase
from django.urls import reverse

from core.tests.factories import (
    project_factory,
    task_type_factory,
    user_factory,
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
