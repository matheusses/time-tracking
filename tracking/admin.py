"""Admin for time-tracking models. Client, Project, TaskType are in project_management."""
from django.contrib import admin

from .models import TimeEntry


@admin.register(TimeEntry)
class TimeEntryAdmin(admin.ModelAdmin):
    list_display = ("user", "project", "task_type", "started_at", "ended_at", "is_active")
    list_filter = ("started_at",)
    search_fields = ("user__username",)
    raw_id_fields = ("user",)
    readonly_fields = ("started_at", "ended_at")
