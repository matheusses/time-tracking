"""
GenerateWeeklyTimesheetUseCase: build weekly timesheet DTO for a user and week.
Calls TimesheetService only; no direct ORM.
"""
from datetime import date

from tracking.application.dtos import TimesheetRowDTO, WeeklyTimesheetDTO
from tracking.domain.services.timesheet_service import TimesheetService


def execute(user_id: int, week_start: date) -> WeeklyTimesheetDTO:
    """
    Return the weekly timesheet for the user: rows (project–task × day totals).
    week_start must be the Monday of the week.
    """
    service = TimesheetService()
    week_start_result, rows_data = service.get_weekly_aggregation(
        user_id=user_id, week_start=week_start
    )
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
