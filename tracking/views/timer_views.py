"""
Timer views and HTMX endpoints. No business logic; call use cases only.
"""
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from project_management.use_cases.get_timer_options import execute as get_timer_options
from tracking.application.dtos import StartTimerInputDTO, StopTimerInputDTO
from tracking.use_cases.get_active_timer import execute as get_active_timer
from tracking.use_cases.start_timer import execute as start_timer_uc
from tracking.use_cases.stop_timer import execute as stop_timer_uc

TIMER_PARTIAL = "tracking/_timer_partial.html"


@login_required
def timer_partial(request: HttpRequest) -> HttpResponse:
    """Return the timer UI fragment (GET). Used for initial load or HTMX refresh."""
    active = get_active_timer(request.user.id)
    timer_options = get_timer_options(
        user_id=request.user.id,
        is_staff=request.user.is_staff,
    )
    return render(
        request,
        TIMER_PARTIAL,
        {"active_timer": active, "timer_options": timer_options},
    )


@login_required
def start_timer(request: HttpRequest) -> HttpResponse:
    """HTMX POST: start a new timer. Returns timer partial HTML."""
    project_id = request.POST.get("project_id") or None
    task_type_id = request.POST.get("task_type_id") or None
    if project_id is not None:
        try:
            project_id = int(project_id)
        except (TypeError, ValueError):
            project_id = None
    if task_type_id is not None:
        try:
            task_type_id = int(task_type_id)
        except (TypeError, ValueError):
            task_type_id = None

    dto = StartTimerInputDTO(
        user_id=request.user.id,
        project_id=project_id,
        task_type_id=task_type_id,
    )
    result = start_timer_uc(dto)
    timer_options = get_timer_options(
        user_id=request.user.id,
        is_staff=request.user.is_staff,
    )
    return render(
        request,
        TIMER_PARTIAL,
        {
            "active_timer": result.active_timer,
            "message": result.message,
            "timer_options": timer_options,
        },
    )


@login_required
def stop_timer(request: HttpRequest) -> HttpResponse:
    """HTMX POST: stop the active timer. Returns timer partial HTML."""
    dto = StopTimerInputDTO(user_id=request.user.id)
    result = stop_timer_uc(dto)
    timer_options = get_timer_options(
        user_id=request.user.id,
        is_staff=request.user.is_staff,
    )
    return render(
        request,
        TIMER_PARTIAL,
        {
            "active_timer": result.active_timer,
            "message": result.message,
            "stopped_duration_seconds": result.stopped_duration_seconds,
            "timer_options": timer_options,
        },
    )
