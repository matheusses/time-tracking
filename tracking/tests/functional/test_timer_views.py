"""Integration tests for timer views and HTMX endpoints. Start timer requires project_id and task_type_id."""
from django.test import Client, TestCase
from django.urls import reverse

from tracking.tests.factories import ProjectFactory, TaskTypeFactory, UserFactory


def _timer_start_post(client, user, project, task_type):
    """POST to timer start with required project/task_type and CSRF."""
    client.force_login(user)
    client.get(reverse("tracking:home"))
    csrf = client.cookies.get("csrftoken")
    data = {"project_id": str(project.id), "task_type_id": str(task_type.id)}
    if csrf:
        data["csrfmiddlewaretoken"] = csrf.value
    return client.post(reverse("tracking:timer_start"), data)


class TimerPartialViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = UserFactory()
        self.project = ProjectFactory(name="P")
        self.task_type = TaskTypeFactory(name="T")

    def test_timer_partial_requires_login(self):
        response = self.client.get(reverse("tracking:timer_partial"))
        self.assertEqual(response.status_code, 302)

    def test_timer_partial_returns_200_when_authenticated(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("tracking:timer_partial"))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Start timer", response.content)

    def test_timer_partial_shows_stop_when_timer_running(self):
        _timer_start_post(self.client, self.user, self.project, self.task_type)
        response = self.client.get(reverse("tracking:timer_partial"))
        self.assertIn(b"Stop", response.content)


class StartTimerViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = UserFactory()
        self.project = ProjectFactory(name="P")
        self.task_type = TaskTypeFactory(name="T")

    def test_start_requires_login(self):
        response = self.client.post(reverse("tracking:timer_start"), {})
        self.assertEqual(response.status_code, 302)

    def test_start_creates_timer_and_returns_partial(self):
        response = _timer_start_post(
            self.client, self.user, self.project, self.task_type
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Stop", response.content)
        self.assertTemplateUsed(response, "tracking/_timer_partial.html")


class StopTimerViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = UserFactory()
        self.project = ProjectFactory(name="P")
        self.task_type = TaskTypeFactory(name="T")

    def test_stop_requires_login(self):
        response = self.client.post(reverse("tracking:timer_stop"), {})
        self.assertEqual(response.status_code, 302)

    def test_stop_returns_partial_with_start_button_when_no_active_timer(self):
        self.client.force_login(self.user)
        self.client.get(reverse("tracking:home"))
        csrf = self.client.cookies.get("csrftoken")
        data = {}
        if csrf:
            data["csrfmiddlewaretoken"] = csrf.value
        response = self.client.post(reverse("tracking:timer_stop"), data)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Start timer", response.content)

    def test_stop_after_start_returns_partial_with_start_button(self):
        _timer_start_post(self.client, self.user, self.project, self.task_type)
        self.client.get(reverse("tracking:home"))
        csrf = self.client.cookies.get("csrftoken")
        data = {}
        if csrf:
            data["csrfmiddlewaretoken"] = csrf.value
        response = self.client.post(reverse("tracking:timer_stop"), data)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Start timer", response.content)
