"""
Presentation layer: Django views and HTMX endpoints.
No business logic; no direct ORM. Calls Application Layer (clients from DI) only.
"""
from django.shortcuts import redirect, render
from django.urls import reverse

from ._clients import pm_client, track_client
from .timer_views import start_timer, stop_timer, timer_partial
from .timesheet_views import (
    get_week_context_for_user,
    timesheet_grid_partial,
    timesheet_page,
    update_time_entry,
)


def home(request):
    """Home page with timer UI and embedded weekly timesheet."""
    if not request.user.is_authenticated:
        login_url = reverse("login")
        next_url = reverse("tracking:home")
        return redirect(f"{login_url}?next={next_url}")

    active_timer = track_client.get_active_timer(request.user.id)
    timer_options = pm_client.get_timer_options(
        user_id=request.user.id,
        is_staff=request.user.is_staff,
    )
    week_context = get_week_context_for_user(
        request.user.id, request.user.is_staff
    )
    context = {
        "active_timer": active_timer,
        "timer_options": timer_options,
        "timesheet_editable": False,
        **week_context,
    }
    return render(request, "tracking/home.html", context)

__all__ = [
    "home",
    "timer_partial",
    "start_timer",
    "stop_timer",
    "timesheet_page",
    "timesheet_grid_partial",
    "update_time_entry",
]
