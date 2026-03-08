"""
TimesheetService: weekly aggregation and update/create of time entries.
DTO in, DTO/domain out. All persistence via TimeEntryRepository (no ORM in service).
Validation of project/task_type uses the upstream client contract (no cross-module repository calls).
"""
from collections import defaultdict
from datetime import date, datetime, timedelta
from typing import Optional

from django.utils import timezone

from tracking.domain.repositories import TimeEntryRepositoryProtocol
from tracking.domain.repositories.time_entry import TimeEntrySummary
from tracking.domain.services.timer_service import ProjectTaskTypeValidatorProtocol
from tracking.infrastructure.repositories import TimeEntryRepository


class TimesheetValidationError(ValueError):
    """Raised when manual entry validation fails (invalid date, project, task, or hours)."""

    def __init__(self, message: str, code: str = "invalid"):
        self.code = code
        super().__init__(message)


def _days_in_week(week_start: date) -> list[date]:
    """Return [Mon, Tue, ..., Sun] for the week starting at week_start."""
    return [week_start + timedelta(days=i) for i in range(7)]


class TimesheetService:
    """
    Domain service for weekly timesheet aggregation and manual entry updates.
    Depends on TimeEntryRepository and optionally a client implementing
    ProjectTaskTypeValidatorProtocol for validation. Does not depend on other modules' repositories.
    """

    def __init__(
        self,
        time_entry_repository: Optional[TimeEntryRepositoryProtocol] = None,
        project_task_type_validator: Optional[ProjectTaskTypeValidatorProtocol] = None,
    ):
        self._time_entry_repo = (
            time_entry_repository if time_entry_repository is not None else TimeEntryRepository()
        )
        self._validator = project_task_type_validator

    def get_weekly_aggregation(
        self,
        user_id: int,
        week_start: date,
    ) -> tuple[date, list[tuple[Optional[int], Optional[int], Optional[str], Optional[str], dict[date, int]]]]:
        """
        Return aggregated time per (project, task_type) per day for the given week.
        week_start is the Monday of the week. Uses repository (single optimized query).
        """
        week_end = week_start + timedelta(days=6)
        entries = self._time_entry_repo.get_entries_for_week(
            user_id=user_id, week_start=week_start, week_end=week_end
        )

        row_map: dict[
            tuple[Optional[int], Optional[int]],
            tuple[Optional[str], Optional[str], dict[date, int]],
        ] = defaultdict(
            lambda: (None, None, {d: 0 for d in _days_in_week(week_start)})
        )

        for entry in entries:
            key = (entry.project_id, entry.task_type_id)
            if key not in row_map:
                row_map[key] = (
                    entry.project_name,
                    entry.task_type_name,
                    {d: 0 for d in _days_in_week(week_start)},
                )
            _, _, day_totals = row_map[key]
            row_map[key] = (entry.project_name, entry.task_type_name, day_totals)
            if entry.started_at_date in day_totals:
                day_totals[entry.started_at_date] += entry.duration_seconds

        rows = [
            (pid, tid, pname, tname, day_totals)
            for (pid, tid), (pname, tname, day_totals) in sorted(row_map.items())
        ]
        return (week_start, rows)

    def user_has_entries_in_week(self, user_id: int, week_start: date) -> bool:
        """Return True if the user has any time entries in the given week (Monday)."""
        return self._time_entry_repo.has_entries_in_week(user_id=user_id, week_start=week_start)

    def update_or_create_entry(
        self,
        user_id: int,
        entry_date: date,
        project_id: Optional[int],
        task_type_id: Optional[int],
        hours: float,
    ) -> TimeEntrySummary:
        """
        Set manual hours for (user, date, project, task_type). Replaces all completed
        entries for that cell with a single manual entry.
        Active (running) timers are left untouched.
        Validates: non-negative hours, project_id/task_type_id exist when provided.
        Returns domain TimeEntrySummary (no ORM).
        """
        if hours < 0:
            raise TimesheetValidationError("Hours must be non-negative.", code="invalid_hours")
        if project_id is None:
            raise TimesheetValidationError("Project is required.", code="missing_project")
        if task_type_id is None:
            raise TimesheetValidationError("Task type is required.", code="missing_task_type")
        if self._validator is not None:
            if not self._validator.project_exists(project_id):
                raise TimesheetValidationError("Invalid project.", code="invalid_project")
            if not self._validator.task_type_exists(task_type_id):
                raise TimesheetValidationError("Invalid task type.", code="invalid_task_type")

        duration_seconds = max(0, int(round(hours * 3600)))
        tz = timezone.get_current_timezone()
        day_start = timezone.make_aware(
            datetime.combine(entry_date, datetime.min.time()), tz
        )

        self._time_entry_repo.delete_completed_for_cell(
            user_id=user_id,
            project_id=project_id,
            task_type_id=task_type_id,
            entry_date=entry_date,
        )
        return self._time_entry_repo.create_manual_entry(
            user_id=user_id,
            project_id=project_id,
            task_type_id=task_type_id,
            started_at=day_start,
            ended_at=day_start,
            manual_duration_seconds=duration_seconds,
        )
