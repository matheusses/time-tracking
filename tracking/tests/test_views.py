"""
Tests for presentation layer (views).
"""
from django.test import Client, TestCase
from django.urls import reverse

from tracking.tests.factories import (
    ProjectFactory,
    TaskTypeFactory,
    UserFactory,
)


class HomeViewTests(TestCase):
    """Test home view: redirects anonymous to login, renders home when authenticated."""

    def setUp(self):
        self.client = Client()

    def test_home_redirects_anonymous_to_login(self):
        response = self.client.get(reverse("tracking:home"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response.url)
        self.assertIn("next=", response.url)

    def test_home_returns_200_when_authenticated(self):
        user = UserFactory()
        self.client.force_login(user)
        response = self.client.get(reverse("tracking:home"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "tracking/home.html")

    def test_home_includes_weekly_timesheet_context(self):
        """Home page includes timesheet data and grid container for authenticated users."""
        user = UserFactory()
        self.client.force_login(user)
        response = self.client.get(reverse("tracking:home"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("timesheet", response.context)
        self.assertIn("week_days", response.context)
        self.assertIn("week_param", response.context)
        self.assertContains(response, "timesheet-grid-container")
        self.assertContains(response, "Weekly timesheet")

    def test_home_selects_first_project_by_default(self):
        """Timer dropdown has the first project selected when projects exist."""
        user = UserFactory(is_staff=True)  # staff so list_projects returns all projects
        project = ProjectFactory()
        self.client.force_login(user)
        response = self.client.get(reverse("tracking:home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, f'value="{project.id}"')
        # Template selects first project (forloop.first); option should have selected
        html = response.content.decode()
        self.assertIn("selected", html)


class TimesheetViewTests(TestCase):
    """Test timesheet page, grid partial, and update endpoint."""

    def setUp(self):
        self.client = Client()
        self.user = UserFactory()

    def test_timesheet_page_requires_login(self):
        response = self.client.get(reverse("tracking:timesheet"))
        self.assertEqual(response.status_code, 302)

    def test_timesheet_page_returns_200_when_authenticated(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("tracking:timesheet"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "tracking/timesheet.html")

    def test_timesheet_page_accepts_week_param(self):
        self.client.force_login(self.user)
        response = self.client.get(
            reverse("tracking:timesheet"),
            {"week": "2025-W10"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Weekly timesheet")

    def test_timesheet_grid_partial_returns_fragment(self):
        self.client.force_login(self.user)
        response = self.client.get(
            reverse("tracking:timesheet_grid"),
            {"week": "2025-W10"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "tracking/_timesheet_grid.html")

    def test_timesheet_grid_partial_editable_0_renders_read_only(self):
        """Grid with editable=0 shows Edit button and no Save; cells are read-only."""
        self.client.force_login(self.user)
        response = self.client.get(
            reverse("tracking:timesheet_grid"),
            {"week": "2025-W10", "editable": "0"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Edit")
        self.assertNotContains(response, "timesheet-save-all")
        self.assertFalse(response.context.get("timesheet_editable"))

    def test_update_time_entry_requires_post(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("tracking:timesheet_update"))
        self.assertEqual(response.status_code, 405)

    def test_update_time_entry_post_creates_or_updates(self):
        self.client.force_login(self.user)
        self.client.get(reverse("tracking:timesheet"))  # set CSRF cookie
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

    def test_update_time_entry_validation_error_returns_cell_with_message(self):
        self.client.force_login(self.user)
        self.client.get(reverse("tracking:timesheet"))
        csrf = self.client.cookies.get("csrftoken")
        post_data = {
            "date": "2025-03-05",
            "project_id": "99999",  # invalid
            "task_type_id": "99999",  # invalid
            "hours": "1",
        }
        if csrf:
            post_data["csrfmiddlewaretoken"] = csrf.value
        response = self.client.post(reverse("tracking:timesheet_update"), post_data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "tracking/_timesheet_cell.html")
        self.assertContains(response, "Invalid", status_code=200)
