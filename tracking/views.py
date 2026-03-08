"""
Presentation layer: Django views and HTMX endpoints.
No business logic; no direct ORM. Calls Application Layer (use_cases) only.
"""
from django.shortcuts import render


def home(request):
    """Placeholder home view until core time-tracking is implemented."""
    return render(request, "tracking/home.html")
