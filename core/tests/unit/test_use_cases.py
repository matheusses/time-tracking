"""
Unit tests for use cases (TrackClient): StartTimer, StopTimer, GenerateWeeklyTimesheet, UpdateTimeEntry.
Input validation, DTO in/out, delegation to services (with real DB; for pure unit tests with mocks see integration).
"""
from datetime import date, datetime

from django.test import TestCase
from django.utils import timezone

from core.di import get_track_client
from core.tests.factories import (
    project_factory,
    task_type_factory,
    time_entry_factory,
    user_factory,
)
from tracking.application.dtos import (
    StartTimerInputDTO,
    StopTimerInputDTO,
    UpdateTimeEntryInputDTO,
)
from tracking.models import TimeEntry


class StartTimerUseCaseTests(TestCase):
    """Test TrackClient.start_timer: input DTO, result DTO, delegation to TimerService."""

    def setUp(self):
        self.user = user_factory()
        self.client = get_track_client()

    def test_start_timer_accepts_dto_returns_timer_result(self):
        dto = StartTimerInputDTO(user_id=self.user.id)
        result = self.client.start_timer(dto)
        self.assertTrue(result.success)
        self.assertIn("started", result.message.lower())
        self.assertIsNotNone(result.active_timer)
        self.assertEqual(
            TimeEntry.objects.filter(user=self.user, ended_at__isnull=True).count(), 1
        )

    def test_start_timer_with_project_and_task_type_in_dto(self):
        project = project_factory(name="P")
        task_type = task_type_factory(name="T")
        dto = StartTimerInputDTO(
            user_id=self.user.id,
            project_id=project.id,
            task_type_id=task_type.id,
        )
        result = self.client.start_timer(dto)
        self.assertTrue(result.success)
        entry = TimeEntry.objects.get(user=self.user, ended_at__isnull=True)
        self.assertEqual(entry.project_id, project.id)
        self.assertEqual(entry.task_type_id, task_type.id)

    def test_start_timer_stops_existing_active_before_creating_new(self):
        self.client.start_timer(StartTimerInputDTO(user_id=self.user.id))
        self.client.start_timer(StartTimerInputDTO(user_id=self.user.id))
        self.assertEqual(
            TimeEntry.objects.filter(user=self.user, ended_at__isnull=True).count(), 1
        )
        self.assertEqual(
            TimeEntry.objects.filter(user=self.user, ended_at__isnull=False).count(), 1
        )


class StopTimerUseCaseTests(TestCase):
    """Test TrackClient.stop_timer: DTO in, result with stopped entry info."""

    def setUp(self):
        self.user = user_factory()
        self.client = get_track_client()

    def test_stop_timer_stops_active_and_returns_success(self):
        self.client.start_timer(StartTimerInputDTO(user_id=self.user.id))
        dto = StopTimerInputDTO(user_id=self.user.id)
        result = self.client.stop_timer(dto)
        self.assertTrue(result.success)
        self.assertIsNone(result.active_timer)
        self.assertEqual(
            TimeEntry.objects.filter(user=self.user, ended_at__isnull=True).count(), 0
        )

    def test_stop_timer_with_no_active_returns_failure_dto(self):
        dto = StopTimerInputDTO(user_id=self.user.id)
        result = self.client.stop_timer(dto)
        self.assertFalse(result.success)
        self.assertIn("No active", result.message)


class GenerateWeeklyTimesheetUseCaseTests(TestCase):
    """Test TrackClient.generate_weekly_timesheet: DTO out, week_start and rows."""

    def setUp(self):
        self.user = user_factory()
        self.client = get_track_client()

    def test_returns_weekly_timesheet_dto_with_week_start_and_rows(self):
        week_start = date(2025, 3, 3)
        dto = self.client.generate_weekly_timesheet(
            self.user.id, week_start, include_empty_rows=False
        )
        self.assertEqual(dto.week_start, week_start)
        self.assertIsInstance(dto.rows, list)

    def test_with_entries_returns_rows_with_day_totals(self):
        project = project_factory()
        task = task_type_factory()
        week_start = date(2025, 3, 3)
        tz = timezone.get_current_timezone()
        time_entry_factory(
            user=self.user,
            project=project,
            task_type=task,
            started_at=timezone.make_aware(datetime(2025, 3, 3, 10, 0), tz),
            ended_at=timezone.make_aware(datetime(2025, 3, 3, 11, 0), tz),
        )
        dto = self.client.generate_weekly_timesheet(
            self.user.id, week_start, include_empty_rows=False
        )
        self.assertEqual(len(dto.rows), 1)
        self.assertEqual(dto.rows[0].project_id, project.id)
        self.assertEqual(dto.rows[0].day_totals.get(week_start, 0), 3600)

    def test_include_empty_rows_adds_all_project_task_combos(self):
        p1 = project_factory(name="P1")
        p2 = project_factory(name="P2")
        t1 = task_type_factory(name="T1")
        t2 = task_type_factory(name="T2")
        week_start = date(2025, 3, 3)
        dto = self.client.generate_weekly_timesheet(
            self.user.id, week_start, is_staff=True, include_empty_rows=True
        )
        self.assertEqual(len(dto.rows), 4)
        row_keys = {(r.project_id, r.task_type_id) for r in dto.rows}
        self.assertEqual(
            row_keys,
            {(p1.id, t1.id), (p1.id, t2.id), (p2.id, t1.id), (p2.id, t2.id)},
        )


class UpdateTimeEntryUseCaseTests(TestCase):
    """Test TrackClient.update_time_entry: input validation, DTO in/out, delegation."""

    def setUp(self):
        self.user = user_factory()
        self.client = get_track_client()

    def test_update_time_entry_creates_entry_returns_summary_dto(self):
        project = project_factory()
        task = task_type_factory()
        dto = UpdateTimeEntryInputDTO(
            user_id=self.user.id,
            date=date(2025, 3, 5),
            project_id=project.id,
            task_type_id=task.id,
            hours=2.0,
        )
        result = self.client.update_time_entry(dto)
        self.assertIsNotNone(result.id)
        self.assertEqual(result.manual_duration_seconds, 7200)
        self.assertEqual(result.user_id, self.user.id)
        self.assertEqual(result.entry_date, date(2025, 3, 5))

    def test_update_time_entry_invalid_project_raises_validation_error(self):
        from tracking.domain.services.timesheet_service import TimesheetValidationError
        task = task_type_factory()
        dto = UpdateTimeEntryInputDTO(
            user_id=self.user.id,
            date=date(2025, 3, 5),
            project_id=99999,
            task_type_id=task.id,
            hours=1.0,
        )
        with self.assertRaises(TimesheetValidationError) as cm:
            self.client.update_time_entry(dto)
        self.assertIn("project", str(cm.exception).lower())

    def test_update_time_entry_invalid_task_type_raises_validation_error(self):
        from tracking.domain.services.timesheet_service import TimesheetValidationError
        project = project_factory()
        dto = UpdateTimeEntryInputDTO(
            user_id=self.user.id,
            date=date(2025, 3, 5),
            project_id=project.id,
            task_type_id=99999,
            hours=1.0,
        )
        with self.assertRaises(TimesheetValidationError) as cm:
            self.client.update_time_entry(dto)
        self.assertIn("task", str(cm.exception).lower())
