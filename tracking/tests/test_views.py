"""
Tests for presentation layer (views).
"""
from django.test import Client, TestCase
from django.urls import reverse


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
