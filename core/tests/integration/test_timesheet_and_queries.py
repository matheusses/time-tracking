"""
Integration tests: weekly timesheet with real DB and assert query count for N+1.
Project/client/task-type listing via services (real DB).
"""
from datetime import date, datetime

from django.test import TestCase
from django.test.utils import CaptureQueriesContext
from django.db import connection
from django.utils import timezone

from core.di import get_track_client
from core.tests.factories import (
    client_factory,
    project_factory,
    task_type_factory,
    time_entry_factory,
    user_factory,
)
from project_management.domain.services.project_service import ProjectService
from tracking.domain.services.timesheet_service import TimesheetService


class WeeklyTimesheetQueryCountIntegrationTests(TestCase):
    """Assert that generating the weekly timesheet does not cause N+1 queries."""

    def setUp(self):
        self.user = user_factory()
        self.week_start = date(2025, 3, 3)
        self.service = TimesheetService()
        # Create several entries across projects/task types
        projects = [project_factory() for _ in range(2)]
        tasks = [task_type_factory() for _ in range(2)]
        tz = timezone.get_current_timezone()
        for i, (p, t) in enumerate([(p, t) for p in projects for t in tasks]):
            time_entry_factory(
                user=self.user,
                project=p,
                task_type=t,
                started_at=timezone.make_aware(
                    datetime(2025, 3, 3 + (i % 3), 10, 0), tz
                ),
                ended_at=timezone.make_aware(
                    datetime(2025, 3, 3 + (i % 3), 11, 0), tz
                ),
            )

    def test_get_weekly_aggregation_bounded_queries(self):
        with CaptureQueriesContext(connection) as ctx:
            self.service.get_weekly_aggregation(self.user.id, self.week_start)
        self.assertLessEqual(
            len(ctx.captured_queries),
            2,
            "Weekly aggregation should use at most 2 queries; got %s"
            % len(ctx.captured_queries),
        )


class ProjectClientTaskTypeServiceIntegrationTests(TestCase):
    """Integration: ProjectService list clients, projects by client, task types with real DB."""

    def setUp(self):
        self.service = ProjectService()
        self.client_a = client_factory(name="Client A")
        self.client_b = client_factory(name="Client B")
        self.project_a1 = project_factory(client=self.client_a, name="Proj A1")
        self.project_a2 = project_factory(client=self.client_a, name="Proj A2")
        self.project_b1 = project_factory(client=self.client_b, name="Proj B1")
        task_type_factory(name="Dev")
        task_type_factory(name="Meeting")

    def test_list_clients_returns_persisted_clients(self):
        rows = self.service.list_clients_for_user(
            user_factory(is_staff=True).id, is_staff=True
        )
        names = [r[1] for r in rows]
        self.assertIn("Client A", names)
        self.assertIn("Client B", names)

    def test_list_projects_by_client_returns_only_that_client_projects(self):
        user = user_factory(is_staff=True)
        rows = self.service.list_projects_for_user(
            user.id, is_staff=True, client_id=self.client_a.id
        )
        self.assertEqual(len(rows), 2)
        names = [r[1] for r in rows]
        self.assertIn("Proj A1", names)
        self.assertIn("Proj A2", names)
        self.assertNotIn("Proj B1", names)

    def test_list_task_types_returns_persisted_task_types(self):
        rows = self.service.list_task_types()
        names = [r[1] for r in rows]
        self.assertIn("Dev", names)
        self.assertIn("Meeting", names)
