"""
TimeEntry repository protocol. Implementations in infrastructure perform ORM access.
All methods take/return domain-friendly types or simple values (no ORM in interface).
"""
from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional, Protocol

from tracking.domain.models import ActiveTimerState


@dataclass(frozen=True)
class EntryForWeek:
    """One time entry row for weekly aggregation (project/task/date/duration)."""

    project_id: Optional[int]
    task_type_id: Optional[int]
    project_name: Optional[str]
    task_type_name: Optional[str]
    started_at_date: date
    duration_seconds: int


@dataclass(frozen=True)
class TimeEntrySummary:
    """Summary of a created/updated time entry (manual or timer). No ORM."""

    id: int
    user_id: int
    project_id: Optional[int]
    task_type_id: Optional[int]
    entry_date: date
    manual_duration_seconds: int


class TimeEntryRepositoryProtocol(Protocol):
    """Repository for TimeEntry domain entity. Only persistence/query; no business rules."""

    def stop_all_active(self, user_id: int, ended_at: datetime) -> None:
        """Set ended_at on all active time entries for the user."""
        ...

    def create(
        self,
        user_id: int,
        project_id: Optional[int],
        task_type_id: Optional[int],
        started_at: datetime,
        ended_at: Optional[datetime] = None,
    ) -> ActiveTimerState:
        """Create a new time entry. Returns active state DTO with names resolved."""
        ...

    def get_active(self, user_id: int) -> Optional[ActiveTimerState]:
        """Return the current active timer state for the user, or None."""
        ...

    def set_ended_at(self, entry_id: int, ended_at: datetime) -> None:
        """Set ended_at for the given entry."""
        ...

    def get_entries_for_week(
        self,
        user_id: int,
        week_start: date,
        week_end: date,
    ) -> list[EntryForWeek]:
        """Return all entries for the user in the date range for aggregation."""
        ...

    def has_entries_in_week(self, user_id: int, week_start: date) -> bool:
        """Return True if the user has any time entries in the given week."""
        ...

    def delete_completed_for_cell(
        self,
        user_id: int,
        project_id: Optional[int],
        task_type_id: Optional[int],
        entry_date: date,
    ) -> None:
        """Delete completed entries for (user, project, task_type, date). Keeps active timers."""
        ...

    def create_manual_entry(
        self,
        user_id: int,
        project_id: Optional[int],
        task_type_id: Optional[int],
        started_at: datetime,
        ended_at: datetime,
        manual_duration_seconds: int,
    ) -> TimeEntrySummary:
        """Create a manual time entry. Returns summary (no ORM)."""
        ...
