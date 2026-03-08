"""Unit tests for timer use cases."""
from django.test import TestCase

from tracking.application.dtos import StartTimerInputDTO, StopTimerInputDTO
from tracking.models import TimeEntry
from tracking.use_cases.start_timer import execute as start_timer
from tracking.use_cases.stop_timer import execute as stop_timer
from tracking.tests.factories import UserFactory


class StartTimerUseCaseTests(TestCase):
    def setUp(self):
        self.user = UserFactory()

    def test_execute_starts_timer(self):
        dto = StartTimerInputDTO(user_id=self.user.id)
        result = start_timer(dto)
        self.assertTrue(result.success)
        self.assertEqual(TimeEntry.objects.filter(user=self.user, ended_at__isnull=True).count(), 1)

    def test_execute_with_project_and_task_type(self):
        from tracking.tests.factories import ProjectFactory, TaskTypeFactory
        project = ProjectFactory(name="P")
        task_type = TaskTypeFactory(name="T")
        dto = StartTimerInputDTO(user_id=self.user.id, project_id=project.id, task_type_id=task_type.id)
        result = start_timer(dto)
        self.assertTrue(result.success)
        entry = TimeEntry.objects.get(user=self.user, ended_at__isnull=True)
        self.assertEqual(entry.project_id, project.id)
        self.assertEqual(entry.task_type_id, task_type.id)


class StopTimerUseCaseTests(TestCase):
    def setUp(self):
        self.user = UserFactory()

    def test_execute_stops_active_timer(self):
        start_timer(StartTimerInputDTO(user_id=self.user.id))
        dto = StopTimerInputDTO(user_id=self.user.id)
        result = stop_timer(dto)
        self.assertTrue(result.success)
        self.assertIsNone(result.active_timer)
        self.assertEqual(TimeEntry.objects.filter(user=self.user, ended_at__isnull=True).count(), 0)

    def test_execute_with_no_active_timer_fails_gracefully(self):
        dto = StopTimerInputDTO(user_id=self.user.id)
        result = stop_timer(dto)
        self.assertFalse(result.success)


class GenerateWeeklyTimesheetUseCaseTests(TestCase):
    """Test GenerateWeeklyTimesheetUseCase returns DTO with week_start and rows."""

    def setUp(self):
        self.user = UserFactory()

    def test_execute_returns_dto_with_week_start_and_rows(self):
        from datetime import date

        from tracking.use_cases.generate_weekly_timesheet import execute as generate_weekly_timesheet

        week_start = date(2025, 3, 3)  # Monday
        dto = generate_weekly_timesheet(self.user.id, week_start)
        self.assertEqual(dto.week_start, week_start)
        self.assertIsInstance(dto.rows, list)

    def test_execute_with_data_returns_rows(self):
        from datetime import date, datetime

        from django.utils import timezone

        from tracking.tests.factories import (
            ProjectFactory,
            TaskTypeFactory,
            TimeEntryFactory,
        )
        from tracking.use_cases.generate_weekly_timesheet import (
            execute as generate_weekly_timesheet,
        )

        project = ProjectFactory()
        task = TaskTypeFactory()
        week_start = date(2025, 3, 3)
        tz = timezone.get_current_timezone()
        TimeEntryFactory(
            user=self.user,
            project=project,
            task_type=task,
            started_at=timezone.make_aware(datetime(2025, 3, 3, 10, 0), tz),
            ended_at=timezone.make_aware(datetime(2025, 3, 3, 11, 0), tz),
        )
        dto = generate_weekly_timesheet(
            self.user.id, week_start, include_empty_rows=False
        )
        self.assertEqual(len(dto.rows), 1)
        self.assertEqual(dto.rows[0].project_id, project.id)
        self.assertEqual(dto.rows[0].day_totals[week_start], 3600)

    def test_execute_with_include_empty_rows_includes_all_project_task_combos(self):
        from datetime import date

        from tracking.tests.factories import ProjectFactory, TaskTypeFactory
        from tracking.use_cases.generate_weekly_timesheet import (
            execute as generate_weekly_timesheet,
        )

        p1 = ProjectFactory(name="P1")
        p2 = ProjectFactory(name="P2")
        t1 = TaskTypeFactory(name="T1")
        t2 = TaskTypeFactory(name="T2")
        week_start = date(2025, 3, 3)
        dto = generate_weekly_timesheet(
            self.user.id, week_start, is_staff=True, include_empty_rows=True
        )
        # Should have 4 rows (2 projects × 2 task types), all with zero totals
        self.assertEqual(len(dto.rows), 4)
        row_keys = {(r.project_id, r.task_type_id) for r in dto.rows}
        self.assertEqual(
            row_keys,
            {(p1.id, t1.id), (p1.id, t2.id), (p2.id, t1.id), (p2.id, t2.id)},
        )
        for row in dto.rows:
            self.assertEqual(sum(row.day_totals.values()), 0)


class UpdateTimeEntryUseCaseTests(TestCase):
    """Test UpdateTimeEntryUseCase creates/updates entry and returns it."""

    def setUp(self):
        self.user = UserFactory()

    def test_execute_creates_entry_and_returns_it(self):
        from datetime import date

        from tracking.application.dtos import UpdateTimeEntryInputDTO
        from tracking.models import TimeEntry
        from tracking.use_cases.update_time_entry import execute as update_time_entry
        from tracking.tests.factories import ProjectFactory, TaskTypeFactory

        project = ProjectFactory()
        task = TaskTypeFactory()
        dto = UpdateTimeEntryInputDTO(
            user_id=self.user.id,
            date=date(2025, 3, 5),
            project_id=project.id,
            task_type_id=task.id,
            hours=2.0,
        )
        entry = update_time_entry(dto)
        self.assertIsNotNone(entry.id)
        self.assertEqual(entry.manual_duration_seconds, 7200)
        self.assertEqual(TimeEntry.objects.filter(user=self.user).count(), 1)

    def test_execute_raises_on_invalid_project_id(self):
        from datetime import date

        from tracking.application.dtos import UpdateTimeEntryInputDTO
        from tracking.domain.services.timesheet_service import TimesheetValidationError
        from tracking.use_cases.update_time_entry import execute as update_time_entry
        from tracking.tests.factories import TaskTypeFactory

        task = TaskTypeFactory()
        dto = UpdateTimeEntryInputDTO(
            user_id=self.user.id,
            date=date(2025, 3, 5),
            project_id=99999,  # does not exist
            task_type_id=task.id,
            hours=1.0,
        )
        with self.assertRaises(TimesheetValidationError) as cm:
            update_time_entry(dto)
        self.assertIn("project", str(cm.exception).lower())

    def test_execute_raises_on_invalid_task_type_id(self):
        from datetime import date

        from tracking.application.dtos import UpdateTimeEntryInputDTO
        from tracking.domain.services.timesheet_service import TimesheetValidationError
        from tracking.use_cases.update_time_entry import execute as update_time_entry
        from tracking.tests.factories import ProjectFactory

        project = ProjectFactory()
        dto = UpdateTimeEntryInputDTO(
            user_id=self.user.id,
            date=date(2025, 3, 5),
            project_id=project.id,
            task_type_id=99999,  # does not exist
            hours=1.0,
        )
        with self.assertRaises(TimesheetValidationError) as cm:
            update_time_entry(dto)
        self.assertIn("task", str(cm.exception).lower())
