"""
DTOs for timer and timesheet use cases. Used by views to pass input and by use cases to return results.
"""
from dataclasses import dataclass
from datetime import date
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


# Result type: use cases return tracking.domain.models.TimerResult (no separate output DTO).


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
