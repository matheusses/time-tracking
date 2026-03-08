"""Integration tests for timer views and HTMX endpoints."""
from django.test import Client, TestCase
from django.urls import reverse

from tracking.tests.factories import UserFactory


class TimerPartialViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = UserFactory()

    def test_timer_partial_requires_login(self):
        response = self.client.get(reverse("tracking:timer_partial"))
        self.assertEqual(response.status_code, 302)

    def test_timer_partial_returns_200_when_authenticated(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("tracking:timer_partial"))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Start timer", response.content)

    def test_timer_partial_shows_stop_when_timer_running(self):
        self.client.force_login(self.user)
        self.client.post(reverse("tracking:timer_start"), {})
        response = self.client.get(reverse("tracking:timer_partial"))
        self.assertIn(b"Stop", response.content)


class StartTimerViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = UserFactory()

    def test_start_requires_login(self):
        response = self.client.post(reverse("tracking:timer_start"), {})
        self.assertEqual(response.status_code, 302)

    def test_start_creates_timer_and_returns_partial(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse("tracking:timer_start"), {})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Stop", response.content)
        self.assertTemplateUsed(response, "tracking/_timer_partial.html")


class StopTimerViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = UserFactory()

    def test_stop_requires_login(self):
        response = self.client.post(reverse("tracking:timer_stop"), {})
        self.assertEqual(response.status_code, 302)

    def test_stop_returns_partial_with_start_button_when_no_active_timer(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse("tracking:timer_stop"), {})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Start timer", response.content)

    def test_stop_after_start_returns_partial_with_start_button(self):
        self.client.force_login(self.user)
        self.client.post(reverse("tracking:timer_start"), {})
        response = self.client.post(reverse("tracking:timer_stop"), {})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Start timer", response.content)
