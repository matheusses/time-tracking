"""
UpdateTimeEntryUseCase: set manual hours for a (user, date, project, task) cell.
Calls TimesheetService only; no direct ORM. Returns DTO (no ORM).
"""
from tracking.application.dtos import TimeEntrySummaryDTO, UpdateTimeEntryInputDTO
from tracking.domain.services.timesheet_service import TimesheetService


def execute(dto: UpdateTimeEntryInputDTO) -> TimeEntrySummaryDTO:
    """
    Update or create the time entry for the given cell (manual hours).
    Returns a DTO summary of the created/updated entry.
    """
    service = TimesheetService()
    summary = service.update_or_create_entry(
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
