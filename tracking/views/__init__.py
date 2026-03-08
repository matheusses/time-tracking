"""
Presentation layer: Django views and HTMX endpoints.
No business logic; no direct ORM. Calls Application Layer (use_cases) only.
"""
from django.shortcuts import render

from project_management.use_cases.get_timer_options import execute as get_timer_options
from tracking.use_cases.get_active_timer import execute as get_active_timer

from .timer_views import start_timer, stop_timer, timer_partial
from .timesheet_views import (
    timesheet_grid_partial,
    timesheet_page,
    update_time_entry,
)


def home(request):
    """Home page with timer UI. Passes active timer state and options for the partial."""
    active_timer = None
    timer_options = None
    if request.user.is_authenticated:
        active_timer = get_active_timer(request.user.id)
        timer_options = get_timer_options(
            user_id=request.user.id,
            is_staff=request.user.is_staff,
        )
    return render(
        request,
        "tracking/home.html",
        {"active_timer": active_timer, "timer_options": timer_options},
    )

__all__ = [
    "home",
    "timer_partial",
    "start_timer",
    "stop_timer",
    "timesheet_page",
    "timesheet_grid_partial",
    "update_time_entry",
]
