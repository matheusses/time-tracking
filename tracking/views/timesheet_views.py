"""
Timesheet views and HTMX endpoints. No business logic; call use cases only.
Supports weekly grid, week navigation (prev/next), and inline cell edit.
"""
from datetime import date, timedelta

from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render

from tracking.application.dtos import UpdateTimeEntryInputDTO
from tracking.domain.services.timesheet_service import TimesheetValidationError
from tracking.use_cases.generate_weekly_timesheet import execute as generate_weekly_timesheet
from tracking.use_cases.has_entries_in_week import execute as has_entries_in_week
from tracking.use_cases.update_time_entry import execute as update_time_entry_uc

TIMESHEET_PAGE = "tracking/timesheet.html"
TIMESHEET_GRID_PARTIAL = "tracking/_timesheet_grid.html"
TIMESHEET_CELL_PARTIAL = "tracking/_timesheet_cell.html"


def _parse_week_param(value: str | None) -> date | None:
    """Parse ?week=YYYY-Www (ISO week) to Monday date. Returns None if invalid."""
    if not value or not value.strip():
        return None
    value = value.strip()
    if len(value) == 10 and value[4] == "-" and value[7] == "-":
        # YYYY-Www
        try:
            from datetime import datetime
            return datetime.strptime(value, "%G-W%V").date()
        except ValueError:
            return None
    return None


def _monday_of_week(d: date) -> date:
    """Return the Monday of the week containing d (ISO week)."""
    return d - timedelta(days=d.weekday())


def _week_range(week_start: date) -> list[date]:
    """Mon..Sun for the given week start."""
    return [week_start + timedelta(days=i) for i in range(7)]


def get_week_context_for_user(
    user_id: int, is_staff: bool, week_start: date | None = None
) -> dict:
    """Build context dict for weekly timesheet (timesheet, week_days, nav params)."""
    if week_start is None:
        week_start = _monday_of_week(date.today())
    timesheet = generate_weekly_timesheet(
        user_id=user_id, week_start=week_start, is_staff=is_staff
    )
    week_days = _week_range(week_start)
    prev_week = week_start - timedelta(days=7)
    next_week = week_start + timedelta(days=7)
    year, week_num, _ = week_start.isocalendar()
    week_param = f"{year}-W{week_num:02d}"
    prev_param = f"{prev_week.isocalendar()[0]}-W{prev_week.isocalendar()[1]:02d}"
    next_param = f"{next_week.isocalendar()[0]}-W{next_week.isocalendar()[1]:02d}"
    current_week_start = _monday_of_week(date.today())
    # Only show/enable prev/next when there is data in that week
    prev_enabled = has_entries_in_week(user_id, prev_week)
    next_enabled = has_entries_in_week(user_id, next_week)
    return {
        "timesheet": timesheet,
        "week_days": week_days,
        "week_start": week_start,
        "prev_week": prev_week,
        "next_week": next_week,
        "week_param": week_param,
        "prev_param": prev_param,
        "next_param": next_param,
        "current_week_start": current_week_start,
        "prev_enabled": prev_enabled,
        "next_enabled": next_enabled,
    }


@login_required
def timesheet_page(request: HttpRequest) -> HttpResponse:
    """Full timesheet page. GET ?week=YYYY-Www (default: current week)."""
    week_start = _parse_week_param(request.GET.get("week"))
    if week_start is None:
        week_start = _monday_of_week(date.today())
    context = get_week_context_for_user(
        request.user.id, request.user.is_staff, week_start
    )
    context["timesheet_editable"] = False
    return render(request, TIMESHEET_PAGE, context)


@login_required
def timesheet_grid_partial(request: HttpRequest) -> HttpResponse:
    """HTMX GET: return only the grid fragment (for week navigation)."""
    week_start = _parse_week_param(request.GET.get("week"))
    if week_start is None:
        week_start = _monday_of_week(date.today())
    context = get_week_context_for_user(
        request.user.id, request.user.is_staff, week_start
    )
    # HTMX can request editable=1 (Edit) or editable=0 (read-only)
    context["timesheet_editable"] = request.GET.get("editable", "0") == "1"
    response = render(request, TIMESHEET_GRID_PARTIAL, context)
    # Ensure Cancel always gets fresh DB state (no cached grid)
    response["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response["Pragma"] = "no-cache"
    return response


@login_required
def update_time_entry(request: HttpRequest) -> HttpResponse:
    """HTMX POST: update or create hours for a cell. Returns cell partial."""
    if request.method != "POST":
        return HttpResponse(status=405)
    try:
        date_str = request.POST.get("date")
        if not date_str:
            return HttpResponse("Missing date", status=400)
        entry_date = date.fromisoformat(date_str)
    except ValueError:
        return HttpResponse("Invalid date", status=400)
    project_id = request.POST.get("project_id")
    task_type_id = request.POST.get("task_type_id")
    if project_id is not None and project_id != "":
        try:
            project_id = int(project_id)
        except (TypeError, ValueError):
            project_id = None
    else:
        project_id = None
    if task_type_id is not None and task_type_id != "":
        try:
            task_type_id = int(task_type_id)
        except (TypeError, ValueError):
            task_type_id = None
    else:
        task_type_id = None
    try:
        hours = float(request.POST.get("hours", "0"))
    except (TypeError, ValueError):
        hours = 0.0
    hours = round(max(0.0, hours), 2)

    dto = UpdateTimeEntryInputDTO(
        user_id=request.user.id,
        date=entry_date,
        project_id=project_id,
        task_type_id=task_type_id,
        hours=hours,
    )
    try:
        update_time_entry_uc(dto)
    except TimesheetValidationError as e:
        # Return cell partial with error so HTMX still swaps and user sees the message
        return render(
            request,
            TIMESHEET_CELL_PARTIAL,
            {
                "total_seconds": max(0, int(round(hours * 3600))),
                "date": entry_date,
                "project_id": project_id,
                "task_type_id": task_type_id,
                "error_message": str(e),
                "timesheet_editable": True,
            },
        )

    # Re-fetch timesheet to get updated totals for that row/day
    week_start = _monday_of_week(entry_date)
    timesheet = generate_weekly_timesheet(
        user_id=request.user.id,
        week_start=week_start,
        is_staff=request.user.is_staff,
    )
    week_days = _week_range(week_start)
    # Find the row and day for the cell
    total_seconds = 0
    for row in timesheet.rows:
        if row.project_id == project_id and row.task_type_id == task_type_id:
            total_seconds = row.day_totals.get(entry_date, 0)
            break
    return render(
        request,
        TIMESHEET_CELL_PARTIAL,
        {
            "total_seconds": total_seconds,
            "date": entry_date,
            "project_id": project_id,
            "task_type_id": task_type_id,
            "timesheet_editable": True,
        },
    )
