"""
Unit tests for TimesheetService: weekly aggregation and update_or_create_entry.
"""
from datetime import date, datetime, timedelta

from django.test import TestCase
from django.utils import timezone

from tracking.domain.services.timesheet_service import TimesheetService, _days_in_week
from tracking.models import TimeEntry
from tracking.tests.factories import (
    ProjectFactory,
    TaskTypeFactory,
    TimeEntryFactory,
    UserFactory,
)


class TimesheetServiceAggregationTests(TestCase):
    """Test get_weekly_aggregation: single query, correct grouping by project/task and day."""

    def setUp(self):
        self.service = TimesheetService()
        self.user = UserFactory()
        # Monday of a fixed week
        self.week_start = date(2025, 3, 3)

    def test_empty_week_returns_no_rows(self):
        week_start, rows = self.service.get_weekly_aggregation(self.user.id, self.week_start)
        self.assertEqual(week_start, self.week_start)
        self.assertEqual(len(rows), 0)

    def test_aggregates_by_project_and_task_type(self):
        project = ProjectFactory(name="P1")
        task = TaskTypeFactory(name="T1")
        # One entry on Monday
        Monday = self.week_start
        TimeEntryFactory(
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
        week_start, rows = self.service.get_weekly_aggregation(self.user.id, self.week_start)
        self.assertEqual(len(rows), 1)
        pid, tid, pname, tname, day_totals = rows[0]
        self.assertEqual(pid, project.id)
        self.assertEqual(tid, task.id)
        self.assertEqual(pname, "P1")
        self.assertEqual(tname, "T1")
        self.assertEqual(day_totals[Monday], 7200)  # 2h

    def test_manual_duration_seconds_included(self):
        project = ProjectFactory()
        task = TaskTypeFactory()
        Monday = self.week_start
        tz = timezone.get_current_timezone()
        day_start = timezone.make_aware(
            datetime(2025, 3, 3, 0, 0),
            tz,
        )
        TimeEntry.objects.create(
            user=self.user,
            project=project,
            task_type=task,
            started_at=day_start,
            ended_at=day_start,
            manual_duration_seconds=3600,
        )
        week_start, rows = self.service.get_weekly_aggregation(self.user.id, self.week_start)
        self.assertEqual(len(rows), 1)
        _, _, _, _, day_totals = rows[0]
        self.assertEqual(day_totals[Monday], 3600)

    def test_multiple_entries_same_cell_summed(self):
        project = ProjectFactory()
        task = TaskTypeFactory()
        Monday = self.week_start
        tz = timezone.get_current_timezone()
        for hour in (9, 14):
            TimeEntryFactory(
                user=self.user,
                project=project,
                task_type=task,
                started_at=timezone.make_aware(
                    datetime(2025, 3, 3, hour, 0),
                    tz,
                ),
                ended_at=timezone.make_aware(
                    datetime(2025, 3, 3, hour + 1, 0),
                    tz,
                ),
            )
        week_start, rows = self.service.get_weekly_aggregation(self.user.id, self.week_start)
        self.assertEqual(len(rows), 1)
        _, _, _, _, day_totals = rows[0]
        self.assertEqual(day_totals[Monday], 7200)  # 1h + 1h

    def test_only_user_entries_included(self):
        project = ProjectFactory()
        task = TaskTypeFactory()
        other_user = UserFactory()
        Monday = self.week_start
        tz = timezone.get_current_timezone()
        TimeEntryFactory(
            user=self.user,
            project=project,
            task_type=task,
            started_at=timezone.make_aware(datetime(2025, 3, 3, 10, 0), tz),
            ended_at=timezone.make_aware(datetime(2025, 3, 3, 11, 0), tz),
        )
        TimeEntryFactory(
            user=other_user,
            project=project,
            task_type=task,
            started_at=timezone.make_aware(datetime(2025, 3, 3, 14, 0), tz),
            ended_at=timezone.make_aware(datetime(2025, 3, 3, 15, 0), tz),
        )
        week_start, rows = self.service.get_weekly_aggregation(self.user.id, self.week_start)
        self.assertEqual(len(rows), 1)
        _, _, _, _, day_totals = rows[0]
        self.assertEqual(day_totals[Monday], 3600)


class TimesheetServiceUpdateOrCreateTests(TestCase):
    """Test update_or_create_entry: create manual entry, update existing."""

    def setUp(self):
        self.service = TimesheetService()
        self.user = UserFactory()
        self.entry_date = date(2025, 3, 5)
        self.project = ProjectFactory()
        self.task = TaskTypeFactory()

    def test_creates_manual_entry_when_none(self):
        entry = self.service.update_or_create_entry(
            user_id=self.user.id,
            entry_date=self.entry_date,
            project_id=self.project.id,
            task_type_id=self.task.id,
            hours=2.5,
        )
        self.assertIsNotNone(entry.id)
        self.assertEqual(entry.manual_duration_seconds, 9000)  # 2.5 * 3600
        self.assertEqual(entry.user_id, self.user.id)
        self.assertEqual(entry.started_at.date(), self.entry_date)

    def test_updates_existing_manual_entry(self):
        self.service.update_or_create_entry(
            user_id=self.user.id,
            entry_date=self.entry_date,
            project_id=self.project.id,
            task_type_id=self.task.id,
            hours=1.0,
        )
        entry = self.service.update_or_create_entry(
            user_id=self.user.id,
            entry_date=self.entry_date,
            project_id=self.project.id,
            task_type_id=self.task.id,
            hours=3.0,
        )
        self.assertEqual(entry.manual_duration_seconds, 10800)
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

    def test_negative_hours_clamped_to_zero(self):
        entry = self.service.update_or_create_entry(
            user_id=self.user.id,
            entry_date=self.entry_date,
            project_id=None,
            task_type_id=None,
            hours=-1.0,
        )
        self.assertEqual(entry.manual_duration_seconds, 0)


class DaysInWeekTests(TestCase):
    def test_returns_seven_days_from_monday(self):
        week_start = date(2025, 3, 3)  # Monday
        days = _days_in_week(week_start)
        self.assertEqual(len(days), 7)
        self.assertEqual(days[0], date(2025, 3, 3))
        self.assertEqual(days[6], date(2025, 3, 9))
