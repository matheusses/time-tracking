"""
Track client: single entry point for tracking use cases.
Views depend on TrackClientInterface only. All logic delegated to domain services
(or orchestration with ProjectManagementClient for weekly timesheet empty rows).
"""
from datetime import date, timedelta
from typing import TYPE_CHECKING, Optional, Protocol

from tracking.application.dtos import (
    StartTimerInputDTO,
    StopTimerInputDTO,
    TimesheetRowDTO,
    UpdateTimeEntryInputDTO,
    WeeklyTimesheetDTO,
    TimeEntrySummaryDTO,
)
from tracking.domain.models import ActiveTimerState, TimerResult
from project_management.domain.repositories import (
    ProjectRepositoryProtocol,
    TaskTypeRepositoryProtocol,
)
from tracking.domain.repositories import TimeEntryRepositoryProtocol
from tracking.domain.services.timer_service import TimerService
from tracking.domain.services.timesheet_service import TimesheetService

if TYPE_CHECKING:
    from project_management.application.clients import ProjectManagementClientInterface


class TrackClientInterface(Protocol):
    """Protocol for the tracking client. All tracking use cases are exposed here."""

    def generate_weekly_timesheet(
        self,
        user_id: int,
        week_start: date,
        *,
        is_staff: bool = False,
        include_empty_rows: bool = True,
    ) -> WeeklyTimesheetDTO:
        """Return the weekly timesheet for the user (with optional empty rows)."""
        ...

    def get_active_timer(self, user_id: int) -> Optional[ActiveTimerState]:
        """Return the current active timer for the user, or None."""
        ...

    def start_timer(self, dto: StartTimerInputDTO) -> TimerResult:
        """Start a new timer; any existing active timer is stopped first."""
        ...

    def stop_timer(self, dto: StopTimerInputDTO) -> TimerResult:
        """Stop the active timer for the user, if any."""
        ...

    def update_time_entry(self, dto: UpdateTimeEntryInputDTO) -> TimeEntrySummaryDTO:
        """Update or create manual hours for a cell. Raises TimesheetValidationError on invalid input."""
        ...

    def has_entries_in_week(self, user_id: int, week_start: date) -> bool:
        """Return True if the user has any time entries in the given week."""
        ...


class TrackClient:
    """
    Client for tracking module. Builds TimerService and TimesheetService from
    repository interfaces; orchestrates weekly timesheet with empty rows via
    ProjectManagementClient. Views call this client only (obtained from DI).
    """

    def __init__(
        self,
        time_entry_repository: TimeEntryRepositoryProtocol,
        project_repository: ProjectRepositoryProtocol,
        task_type_repository: TaskTypeRepositoryProtocol,
        project_management_client: "ProjectManagementClientInterface",
    ) -> None:
        self._timer_service = TimerService(
            time_entry_repository=time_entry_repository,
        )
        self._timesheet_service = TimesheetService(
            time_entry_repository=time_entry_repository,
            project_repository=project_repository,
            task_type_repository=task_type_repository,
        )
        self._project_management_client = project_management_client

    def generate_weekly_timesheet(
        self,
        user_id: int,
        week_start: date,
        *,
        is_staff: bool = False,
        include_empty_rows: bool = True,
    ) -> WeeklyTimesheetDTO:
        """
        Return the weekly timesheet for the user: rows (project–task × day totals).
        When include_empty_rows is True, includes all (project × task_type) combinations
        via ProjectManagementClient so users can add manual hours in any cell.
        """
        week_start_result, rows_data = self._timesheet_service.get_weekly_aggregation(
            user_id=user_id, week_start=week_start
        )
        data_by_key = {
            (pid, tid): (pname, tname, day_totals)
            for (pid, tid, pname, tname, day_totals) in rows_data
        }

        if include_empty_rows:
            projects = self._project_management_client.list_projects(
                user_id=user_id, is_staff=is_staff
            )
            task_types = self._project_management_client.list_task_types()
            week_days = [week_start + timedelta(days=i) for i in range(7)]
            empty_totals = {d: 0 for d in week_days}
            for p in projects:
                for t in task_types:
                    key = (p.id, t.id)
                    if key not in data_by_key:
                        data_by_key[key] = (p.name, t.name, empty_totals.copy())
            rows_data = [
                (pid, tid, pname, tname, day_totals)
                for (pid, tid), (pname, tname, day_totals) in sorted(data_by_key.items())
            ]

        rows = [
            TimesheetRowDTO(
                project_id=pid,
                task_type_id=tid,
                project_name=pname,
                task_type_name=tname,
                day_totals=day_totals,
            )
            for (pid, tid, pname, tname, day_totals) in rows_data
        ]
        return WeeklyTimesheetDTO(week_start=week_start_result, rows=rows)

    def get_active_timer(self, user_id: int) -> Optional[ActiveTimerState]:
        """Return the current active timer for the user, or None."""
        return self._timer_service.get_active_timer(user_id=user_id)

    def start_timer(self, dto: StartTimerInputDTO) -> TimerResult:
        """Start a new timer for the user. Any existing active timer is stopped first."""
        return self._timer_service.start(
            user_id=dto.user_id,
            project_id=dto.project_id,
            task_type_id=dto.task_type_id,
        )

    def stop_timer(self, dto: StopTimerInputDTO) -> TimerResult:
        """Stop the active timer for the user, if any."""
        return self._timer_service.stop(user_id=dto.user_id)

    def update_time_entry(self, dto: UpdateTimeEntryInputDTO) -> TimeEntrySummaryDTO:
        """
        Update or create manual hours for the given cell.
        Raises TimesheetValidationError on invalid input.
        """
        summary = self._timesheet_service.update_or_create_entry(
            user_id=dto.user_id,
            entry_date=dto.date,
            project_id=dto.project_id,
            task_type_id=dto.task_type_id,
            hours=dto.hours,
        )
        return TimeEntrySummaryDTO(
            id=summary.id,
            user_id=summary.user_id,
            project_id=summary.project_id,
            task_type_id=summary.task_type_id,
            entry_date=summary.entry_date,
            manual_duration_seconds=summary.manual_duration_seconds,
        )

    def has_entries_in_week(self, user_id: int, week_start: date) -> bool:
        """Return True if the user has any time entries in the given week (Monday)."""
        return self._timesheet_service.user_has_entries_in_week(
            user_id=user_id, week_start=week_start
        )
