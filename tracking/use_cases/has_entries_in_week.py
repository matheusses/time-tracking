"""
HasEntriesInWeekUseCase: check if a user has any time entries in a given week.
Calls TimesheetService only; no direct ORM.
"""
from datetime import date

from tracking.domain.services.timesheet_service import TimesheetService


def execute(user_id: int, week_start: date) -> bool:
    """Return True if the user has at least one time entry in the week (week_start = Monday)."""
    service = TimesheetService()
    return service.user_has_entries_in_week(user_id=user_id, week_start=week_start)
