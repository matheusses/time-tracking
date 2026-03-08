"""Custom template filters for timesheet and tracking templates."""
from django import template

register = template.Library()


@register.filter
def get_item(d, key):
    """Return d.get(key, 0) for use in templates (e.g. row.day_totals|get_item:day)."""
    if d is None:
        return 0
    return d.get(key, 0)


@register.filter
def duration_hours(seconds):
    """Format seconds as hours for display (e.g. 9000 -> '2.5'). Returns '—' if zero or None."""
    if seconds is None or seconds == 0:
        return "—"
    return f"{seconds / 3600:.1f}"


@register.filter
def seconds_to_hours(seconds):
    """Convert seconds to numeric hours for input value (e.g. 9000 -> 2.5)."""
    if seconds is None or seconds == 0:
        return 0
    return round(seconds / 3600, 2)
