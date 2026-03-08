"""
Functional tests: security and negative cases.
Invalid CSRF, invalid payloads, unauthorized access. Aligned with OWASP concerns.
"""
from django.test import Client, TestCase
from django.urls import reverse

from core.tests.factories import user_factory


class CSRFProtectionTests(TestCase):
    """POST without valid CSRF token should be rejected (Django returns 403)."""

    def setUp(self):
        # Enforce CSRF so that missing or invalid token returns 403
        self.client = Client(enforce_csrf_checks=True)
        self.user = user_factory()

    def test_timer_start_post_without_csrf_returns_403(self):
        self.client.force_login(self.user)
        # Do not call get() first so no CSRF cookie; or omit token
        response = self.client.post(reverse("tracking:timer_start"), {})
        self.assertEqual(response.status_code, 403)

    def test_timesheet_update_post_with_wrong_csrf_returns_403(self):
        self.client.force_login(self.user)
        self.client.get(reverse("tracking:timesheet"))
        response = self.client.post(
            reverse("tracking:timesheet_update"),
            {
                "csrfmiddlewaretoken": "invalid-token",
                "date": "2025-03-05",
                "project_id": "",
                "task_type_id": "",
                "hours": "1",
            },
        )
        self.assertEqual(response.status_code, 403)


class InvalidPayloadTests(TestCase):
    """Invalid payloads: bad date, bad hours, missing required fields."""

    def setUp(self):
        self.client = Client()
        self.user = user_factory()

    def test_timesheet_update_invalid_date_returns_400(self):
        self.client.force_login(self.user)
        self.client.get(reverse("tracking:timesheet"))
        csrf = self.client.cookies.get("csrftoken")
        post_data = {
            "date": "not-a-date",
            "project_id": "",
            "task_type_id": "",
            "hours": "1",
        }
        if csrf:
            post_data["csrfmiddlewaretoken"] = csrf.value
        response = self.client.post(reverse("tracking:timesheet_update"), post_data)
        self.assertEqual(response.status_code, 400)

    def test_timesheet_update_missing_date_returns_400(self):
        self.client.force_login(self.user)
        self.client.get(reverse("tracking:timesheet"))
        csrf = self.client.cookies.get("csrftoken")
        post_data = {
            "project_id": "",
            "task_type_id": "",
            "hours": "1",
        }
        if csrf:
            post_data["csrfmiddlewaretoken"] = csrf.value
        response = self.client.post(reverse("tracking:timesheet_update"), post_data)
        self.assertEqual(response.status_code, 400)


class UnauthorizedAccessTests(TestCase):
    """Unauthenticated access to protected endpoints returns redirect to login."""

    def setUp(self):
        self.client = Client()

    def test_home_redirects_anonymous_to_login(self):
        response = self.client.get(reverse("tracking:home"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response.url)

    def test_timer_start_redirects_anonymous_to_login(self):
        response = self.client.post(reverse("tracking:timer_start"), {})
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response.url)

    def test_timesheet_page_redirects_anonymous_to_login(self):
        response = self.client.get(reverse("tracking:timesheet"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response.url)

    def test_timesheet_update_post_redirects_anonymous_to_login(self):
        response = self.client.post(
            reverse("tracking:timesheet_update"),
            {"date": "2025-03-05", "hours": "1"},
        )
        self.assertEqual(response.status_code, 302)


class MethodNotAllowedTests(TestCase):
    """Wrong HTTP method where only POST is allowed."""

    def setUp(self):
        self.client = Client()
        self.user = user_factory()

    def test_timesheet_update_get_returns_405(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("tracking:timesheet_update"))
        self.assertEqual(response.status_code, 405)
