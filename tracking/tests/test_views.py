"""
Tests for presentation layer (views).
"""
from django.test import Client, TestCase
from django.urls import reverse

from tracking.tests.factories import UserFactory


class HomeViewTests(TestCase):
    """Test home view returns 200 and uses correct template."""

    def setUp(self):
        self.client = Client()

    def test_home_returns_200(self):
        response = self.client.get(reverse("tracking:home"))
        self.assertEqual(response.status_code, 200)

    def test_home_uses_home_template(self):
        response = self.client.get(reverse("tracking:home"))
        self.assertTemplateUsed(response, "tracking/home.html")


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
