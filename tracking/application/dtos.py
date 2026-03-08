"""
DTOs for timer and timesheet use cases. Used by views to pass input and by use cases to return results.
"""
from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional


@dataclass(frozen=True)
class StartTimerInputDTO:
    """Input for starting a timer."""

    user_id: int
    project_id: Optional[int] = None
    task_type_id: Optional[int] = None


@dataclass(frozen=True)
class StopTimerInputDTO:
    """Input for stopping the active timer."""

    user_id: int


# --- Timer output DTOs (service return types; use cases may use domain TimerResult or these) ---


@dataclass(frozen=True)
class ActiveTimerStateDTO:
    """Active timer state for API/views. Mirrors domain ActiveTimerState."""

    entry_id: int
    project_id: Optional[int]
    project_name: Optional[str]
    task_type_id: Optional[int]
    task_type_name: Optional[str]
    started_at: datetime


@dataclass(frozen=True)
class TimerResultDTO:
    """Result of start/stop timer. Mirrors domain TimerResult."""

    success: bool
    message: str
    active_timer: Optional[ActiveTimerStateDTO] = None
    stopped_entry_id: Optional[int] = None
    stopped_duration_seconds: Optional[int] = None


# --- Timesheet DTOs ---


@dataclass(frozen=True)
class TimesheetRowDTO:
    """One row in the weekly grid: project + task type and per-day totals (seconds)."""

    project_id: Optional[int]
    task_type_id: Optional[int]
    project_name: Optional[str]
    task_type_name: Optional[str]
    day_totals: dict[date, int]


@dataclass(frozen=True)
class WeeklyTimesheetDTO:
    """Weekly timesheet: week start (Monday) and rows (project-task × day totals)."""

    week_start: date
    rows: list[TimesheetRowDTO]


@dataclass(frozen=True)
class UpdateTimeEntryInputDTO:
    """Input for updating or creating a time entry (manual hours) for a cell."""

    user_id: int
    date: date
    project_id: Optional[int]
    task_type_id: Optional[int]
    hours: float


@dataclass(frozen=True)
class TimeEntrySummaryDTO:
    """Summary of a time entry after create/update (manual hours). No ORM."""

    id: int
    user_id: int
    project_id: Optional[int]
    task_type_id: Optional[int]
    entry_date: date
    manual_duration_seconds: int


# --- DTO validators (no-op or minimal checks; used when building DTOs in clients) ---


def validate_time_entry_summary_dto(dto: TimeEntrySummaryDTO) -> None:
    """Validate TimeEntrySummaryDTO structure. No-op for now."""
    assert dto.id >= 0 and dto.manual_duration_seconds >= 0


def validate_timesheet_row_dto(
    project_id: Optional[int],
    task_type_id: Optional[int],
    project_name: Optional[str],
    task_type_name: Optional[str],
    day_totals: dict,
) -> None:
    """Validate row data for TimesheetRowDTO. No-op for now."""
    assert isinstance(day_totals, dict)


def validate_weekly_timesheet_dto(week_start: date, rows: list) -> None:
    """Validate WeeklyTimesheetDTO structure. No-op for now."""
    assert isinstance(rows, list)
