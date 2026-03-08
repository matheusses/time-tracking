"""
TimesheetService: weekly aggregation and update/create of time entries.
Efficient queries to avoid N+1 when building the weekly grid.
Validation: non-negative hours, valid date, project_id/task_type_id must exist when provided.
"""
from collections import defaultdict
from datetime import date, datetime, timedelta
from typing import Optional

from django.utils import timezone

from project_management.models import Project, TaskType
from tracking.models import TimeEntry


class TimesheetValidationError(ValueError):
    """Raised when manual entry validation fails (invalid date, project, task, or hours)."""

    def __init__(self, message: str, code: str = "invalid"):
        self.code = code
        super().__init__(message)


class TimesheetService:
    """
    Domain service for weekly timesheet aggregation and manual entry updates.
    All ORM access for timesheet operations is centralized here.
    """

    def get_weekly_aggregation(
        self,
        user_id: int,
        week_start: date,
    ) -> tuple[date, list[tuple[Optional[int], Optional[int], Optional[str], Optional[str], dict[date, int]]]]:
        """
        Return aggregated time per (project, task_type) per day for the given week.
        week_start is the Monday of the week. Uses a single optimized query (no N+1).
        """
        week_end = week_start + timedelta(days=6)
        # Single query: all entries for user in the week, with related project/task_type
        entries = (
            TimeEntry.objects.filter(
                user_id=user_id,
                started_at__date__gte=week_start,
                started_at__date__lte=week_end,
            )
            .select_related("project", "task_type")
            .order_by("project_id", "task_type_id", "started_at")
        )

        # (project_id, task_type_id) -> (project_name, task_type_name, day_totals)
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
                    entry.project.name if entry.project else None,
                    entry.task_type.name if entry.task_type else None,
                    {d: 0 for d in _days_in_week(week_start)},
                )
            _, _, day_totals = row_map[key]
            # Update names in case we had None from a previous entry
            pname = entry.project.name if entry.project else None
            tname = entry.task_type.name if entry.task_type else None
            row_map[key] = (pname, tname, day_totals)
            entry_date = entry.started_at.date()
            duration = entry.duration_seconds or 0
            if entry_date in day_totals:
                day_totals[entry_date] += duration

        rows = [
            (pid, tid, pname, tname, day_totals)
            for (pid, tid), (pname, tname, day_totals) in sorted(row_map.items())
        ]
        return (week_start, rows)

    def user_has_entries_in_week(self, user_id: int, week_start: date) -> bool:
        """Return True if the user has any time entries in the given week (Monday)."""
        week_end = week_start + timedelta(days=6)
        return TimeEntry.objects.filter(
            user_id=user_id,
            started_at__date__gte=week_start,
            started_at__date__lte=week_end,
        ).exists()

    def update_or_create_entry(
        self,
        user_id: int,
        entry_date: date,
        project_id: Optional[int],
        task_type_id: Optional[int],
        hours: float,
    ) -> TimeEntry:
        """
        Set manual hours for (user, date, project, task_type). Creates a manual entry
        or updates the existing one for that cell. Other timer entries for the same
        (user, date, project, task) are left as-is (totals sum).
        Validates: non-negative hours, project_id/task_type_id exist when provided.
        """
        if hours < 0:
            raise TimesheetValidationError("Hours must be non-negative.", code="invalid_hours")
        if project_id is not None and not Project.objects.filter(pk=project_id).exists():
            raise TimesheetValidationError("Invalid project.", code="invalid_project")
        if task_type_id is not None and not TaskType.objects.filter(pk=task_type_id).exists():
            raise TimesheetValidationError("Invalid task type.", code="invalid_task_type")

        duration_seconds = max(0, int(round(hours * 3600)))
        # Use noon on the date to avoid timezone boundary issues
        tz = timezone.get_current_timezone()
        day_start = timezone.make_aware(
            datetime.combine(entry_date, datetime.min.time()), tz
        )
        # Find existing manual entry for this (user, date, project, task)
        manual = (
            TimeEntry.objects.filter(
                user_id=user_id,
                project_id=project_id,
                task_type_id=task_type_id,
                started_at__date=entry_date,
                ended_at__date=entry_date,
                manual_duration_seconds__isnull=False,
            )
            .order_by("id")
            .first()
        )
        if manual:
            manual.manual_duration_seconds = duration_seconds
            manual.save(update_fields=["manual_duration_seconds"])
            return manual
        # Create new manual entry
        return TimeEntry.objects.create(
            user_id=user_id,
            project_id=project_id,
            task_type_id=task_type_id,
            started_at=day_start,
            ended_at=day_start,
            manual_duration_seconds=duration_seconds,
        )


def _days_in_week(week_start: date) -> list[date]:
    """Return [Mon, Tue, ..., Sun] for the week starting at week_start."""
    return [week_start + timedelta(days=i) for i in range(7)]