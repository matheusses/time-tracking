"""
Unit tests for TimesheetService: weekly aggregation, N+1 assertion, get-or-create manual entry.
"""
from datetime import date, datetime, timedelta

from django.test import TestCase
from django.utils import timezone

from core.tests.factories import (
    project_factory,
    task_type_factory,
    time_entry_factory,
    user_factory,
)
from tracking.domain.services.timesheet_service import (
    TimesheetService,
    TimesheetValidationError,
    _days_in_week,
)


class TimesheetServiceAggregationTests(TestCase):
    """Test get_weekly_aggregation: single query for grid data (no N+1), correct grouping."""

    def setUp(self):
        self.service = TimesheetService()
        self.user = user_factory()
        self.week_start = date(2025, 3, 3)  # Monday

    def test_empty_week_returns_no_rows(self):
        week_start, rows = self.service.get_weekly_aggregation(
            self.user.id, self.week_start
        )
        self.assertEqual(week_start, self.week_start)
        self.assertEqual(len(rows), 0)

    def test_aggregates_by_project_and_task_type(self):
        project = project_factory(name="P1")
        task = task_type_factory(name="T1")
        Monday = self.week_start
        time_entry_factory(
            user=self.user,
            project=project,
            task_type=task,
            started_at=timezone.make_aware(
                datetime(2025, 3, 3, 10, 0),
                timezone.get_current_timezone(),
            ),
            ended_at=timezone.make_aware(
                datetime(2025, 3, 3, 12, 0),
                timezone.get_current_timezone(),
            ),
        )
        week_start, rows = self.service.get_weekly_aggregation(
            self.user.id, self.week_start
        )
        self.assertEqual(len(rows), 1)
        pid, tid, pname, tname, day_totals = rows[0]
        self.assertEqual(pid, project.id)
        self.assertEqual(tid, task.id)
        self.assertEqual(pname, "P1")
        self.assertEqual(tname, "T1")
        self.assertEqual(day_totals[Monday], 7200)  # 2h

    def test_get_weekly_aggregation_single_query_no_n_plus_one(self):
        """Assert that get_weekly_aggregation uses a single query for grid data (no N+1)."""
        from django.test.utils import CaptureQueriesContext
        from django.db import connection
        project = project_factory()
        task = task_type_factory()
        tz = timezone.get_current_timezone()
        for i in range(3):
            time_entry_factory(
                user=self.user,
                project=project,
                task_type=task,
                started_at=timezone.make_aware(
                    datetime(2025, 3, 3 + i, 10, 0), tz
                ),
                ended_at=timezone.make_aware(
                    datetime(2025, 3, 3 + i, 11, 0), tz
                ),
            )
        with CaptureQueriesContext(connection) as ctx:
            self.service.get_weekly_aggregation(self.user.id, self.week_start)
        # One main query for entries (select_related project/task_type avoids N+1 per row)
        self.assertLessEqual(
            len(ctx.captured_queries),
            2,
            "get_weekly_aggregation should use at most 2 queries; got %s"
            % len(ctx.captured_queries),
        )

    def test_multiple_entries_same_cell_summed(self):
        project = project_factory()
        task = task_type_factory()
        Monday = self.week_start
        tz = timezone.get_current_timezone()
        for hour in (9, 14):
            time_entry_factory(
                user=self.user,
                project=project,
                task_type=task,
                started_at=timezone.make_aware(
                    datetime(2025, 3, 3, hour, 0), tz
                ),
                ended_at=timezone.make_aware(
                    datetime(2025, 3, 3, hour + 1, 0), tz
                ),
            )
        week_start, rows = self.service.get_weekly_aggregation(
            self.user.id, self.week_start
        )
        self.assertEqual(len(rows), 1)
        _, _, _, _, day_totals = rows[0]
        self.assertEqual(day_totals[Monday], 7200)  # 1h + 1h

    def test_only_user_entries_included(self):
        project = project_factory()
        task = task_type_factory()
        other_user = user_factory()
        Monday = self.week_start
        tz = timezone.get_current_timezone()
        time_entry_factory(
            user=self.user,
            project=project,
            task_type=task,
            started_at=timezone.make_aware(datetime(2025, 3, 3, 10, 0), tz),
            ended_at=timezone.make_aware(datetime(2025, 3, 3, 11, 0), tz),
        )
        time_entry_factory(
            user=other_user,
            project=project,
            task_type=task,
            started_at=timezone.make_aware(datetime(2025, 3, 3, 14, 0), tz),
            ended_at=timezone.make_aware(datetime(2025, 3, 3, 15, 0), tz),
        )
        week_start, rows = self.service.get_weekly_aggregation(
            self.user.id, self.week_start
        )
        self.assertEqual(len(rows), 1)
        _, _, _, _, day_totals = rows[0]
        self.assertEqual(day_totals[Monday], 3600)


class TimesheetServiceUpdateOrCreateTests(TestCase):
    """Test update_or_create_entry: get-or-create for manual entry, validation."""

    def setUp(self):
        self.service = TimesheetService()
        self.user = user_factory()
        self.entry_date = date(2025, 3, 5)
        self.project = project_factory()
        self.task = task_type_factory()

    def test_creates_manual_entry_when_none(self):
        summary = self.service.update_or_create_entry(
            user_id=self.user.id,
            entry_date=self.entry_date,
            project_id=self.project.id,
            task_type_id=self.task.id,
            hours=2.5,
        )
        self.assertIsNotNone(summary.id)
        self.assertEqual(summary.manual_duration_seconds, 9000)  # 2.5 * 3600
        self.assertEqual(summary.user_id, self.user.id)
        self.assertEqual(summary.entry_date, self.entry_date)

    def test_updates_existing_manual_entry(self):
        self.service.update_or_create_entry(
            user_id=self.user.id,
            entry_date=self.entry_date,
            project_id=self.project.id,
            task_type_id=self.task.id,
            hours=1.0,
        )
        summary = self.service.update_or_create_entry(
            user_id=self.user.id,
            entry_date=self.entry_date,
            project_id=self.project.id,
            task_type_id=self.task.id,
            hours=3.0,
        )
        self.assertEqual(summary.manual_duration_seconds, 10800)
        from tracking.models import TimeEntry
        self.assertEqual(
            TimeEntry.objects.filter(
                user=self.user,
                started_at__date=self.entry_date,
                project=self.project,
                task_type=self.task,
                manual_duration_seconds__isnull=False,
            ).count(),
            1,
        )

    def test_negative_hours_raises_validation_error(self):
        with self.assertRaises(TimesheetValidationError) as cm:
            self.service.update_or_create_entry(
                user_id=self.user.id,
                entry_date=self.entry_date,
                project_id=None,
                task_type_id=None,
                hours=-1.0,
            )
        self.assertIn("non-negative", str(cm.exception))

    def test_invalid_project_id_raises_validation_error(self):
        with self.assertRaises(TimesheetValidationError) as cm:
            self.service.update_or_create_entry(
                user_id=self.user.id,
                entry_date=self.entry_date,
                project_id=99999,
                task_type_id=self.task.id,
                hours=1.0,
            )
        self.assertIn("project", str(cm.exception).lower())

    def test_invalid_task_type_id_raises_validation_error(self):
        with self.assertRaises(TimesheetValidationError) as cm:
            self.service.update_or_create_entry(
                user_id=self.user.id,
                entry_date=self.entry_date,
                project_id=self.project.id,
                task_type_id=99999,
                hours=1.0,
            )
        self.assertIn("task", str(cm.exception).lower())


class UserHasEntriesInWeekTests(TestCase):
    """Test user_has_entries_in_week."""

    def setUp(self):
        self.service = TimesheetService()
        self.user = user_factory()
        self.week_start = date(2025, 3, 3)

    def test_empty_week_returns_false(self):
        self.assertFalse(
            self.service.user_has_entries_in_week(self.user.id, self.week_start)
        )

    def test_week_with_entry_returns_true(self):
        project = project_factory()
        task = task_type_factory()
        tz = timezone.get_current_timezone()
        day_start = timezone.make_aware(datetime(2025, 3, 3, 10, 0), tz)
        time_entry_factory(
            user=self.user,
            project=project,
            task_type=task,
            started_at=day_start,
            ended_at=day_start + timedelta(hours=1),
        )
        self.assertTrue(
            self.service.user_has_entries_in_week(self.user.id, self.week_start)
        )


class DaysInWeekTests(TestCase):
    def test_returns_seven_days_from_monday(self):
        week_start = date(2025, 3, 3)
        days = _days_in_week(week_start)
        self.assertEqual(len(days), 7)
        self.assertEqual(days[0], date(2025, 3, 3))
        self.assertEqual(days[6], date(2025, 3, 9))
