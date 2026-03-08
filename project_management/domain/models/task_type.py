"""
Task Type model. Used as options for timer/timesheet (e.g. Design, Development, Meeting).
CRUD is admin-only; listed for dropdowns via ProjectService/use cases.
"""
from django.db import models


class TaskType(models.Model):
    """Type of work for time entries (e.g. Design, Development, Meeting)."""

    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Task type"
        verbose_name_plural = "Task types"

    def __str__(self):
        return self.name
