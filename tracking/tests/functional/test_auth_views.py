"""
Tests for authentication views (login/logout).
Uses Django's built-in auth URLs at /accounts/.
"""
from django.test import Client, TestCase
from django.urls import reverse

from tracking.tests.factories import UserFactory


class LoginViewTests(TestCase):
    """Test login page and login flow."""

    def setUp(self):
        self.client = Client()

    def test_login_page_returns_200(self):
        response = self.client.get(reverse("login"))
        self.assertEqual(response.status_code, 200)

    def test_login_page_uses_registration_template(self):
        response = self.client.get(reverse("login"))
        self.assertTemplateUsed(response, "registration/login.html")

    def test_login_page_contains_username_and_password_fields(self):
        response = self.client.get(reverse("login"))
        self.assertContains(response, "id_username")
        self.assertContains(response, "id_password")
        self.assertContains(response, "Log in")

    def test_login_with_valid_credentials_redirects_to_home(self):
        user = UserFactory(username="jane", password="testpass123!")
        response = self.client.post(
            reverse("login"),
            {"username": "jane", "password": "testpass123!"},
            follow=False,
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/")

    def test_login_with_invalid_credentials_returns_200_with_errors(self):
        response = self.client.post(
            reverse("login"),
            {"username": "nobody", "password": "wrong"},
            follow=False,
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "registration/login.html")
        self.assertContains(response, "Log in")
        self.assertTrue(response.context["form"].errors)

    def test_login_redirects_to_next_param_when_provided(self):
        user = UserFactory(username="bob", password="testpass123!")
        response = self.client.post(
            reverse("login") + "?next=/timesheet/",
            {"username": "bob", "password": "testpass123!"},
            follow=False,
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/timesheet/")


class LogoutViewTests(TestCase):
    """Test logout redirect."""

    def setUp(self):
        self.client = Client()
        self.user = UserFactory()

    def test_logout_redirects_to_home(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse("logout"), follow=False)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/")
