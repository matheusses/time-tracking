"""
GenerateWeeklyTimesheetUseCase: build weekly timesheet DTO for a user and week.
Calls TimesheetService only; no direct ORM.
Includes empty (project × task) rows so users can add manual hours in any cell.
"""
from datetime import date, timedelta

from project_management.use_cases.list_projects import execute as list_projects
from project_management.use_cases.list_task_types import execute as list_task_types

from tracking.application.dtos import TimesheetRowDTO, WeeklyTimesheetDTO
from tracking.domain.services.timesheet_service import TimesheetService


def execute(
    user_id: int,
    week_start: date,
    *,
    is_staff: bool = False,
    include_empty_rows: bool = True,
) -> WeeklyTimesheetDTO:
    """
    Return the weekly timesheet for the user: rows (project–task × day totals).
    week_start must be the Monday of the week.
    When include_empty_rows is True, includes all (project × task_type) combinations
    so users can add manual hours in cells that have no entry yet.
    """
    service = TimesheetService()
    week_start_result, rows_data = service.get_weekly_aggregation(
        user_id=user_id, week_start=week_start
    )
    data_by_key = {
        (pid, tid): (pname, tname, day_totals)
        for (pid, tid, pname, tname, day_totals) in rows_data
    }

    if include_empty_rows:
        projects = list_projects(user_id=user_id, is_staff=is_staff)
        task_types = list_task_types()
        week_days = [week_start + timedelta(days=i) for i in range(7)]
        empty_totals = {d: 0 for d in week_days}
        for p in projects:
            for t in task_types:
                key = (p.id, t.id)
                if key not in data_by_key:
                    data_by_key[key] = (p.name, t.name, empty_totals.copy())
        # Rebuild rows: all keys sorted, with merged data
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
