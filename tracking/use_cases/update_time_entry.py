"""
UpdateTimeEntryUseCase: set manual hours for a (user, date, project, task) cell.
Calls TimesheetService only; no direct ORM.
"""
from tracking.application.dtos import UpdateTimeEntryInputDTO
from tracking.domain.services.timesheet_service import TimesheetService
from tracking.models import TimeEntry


def execute(dto: UpdateTimeEntryInputDTO) -> TimeEntry:
    """
    Update or create the time entry for the given cell (manual hours).
    Returns the created or updated TimeEntry.
    """
    service = TimesheetService()
    return service.update_or_create_entry(
        user_id=dto.user_id,
        entry_date=dto.date,
        project_id=dto.project_id,
        task_type_id=dto.task_type_id,
        hours=dto.hours,
    )
