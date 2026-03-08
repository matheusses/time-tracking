"""
Django ORM models for the tracking app.
Persistence models used by domain services only; see tracking.domain.services.
Project and TaskType come from project_management app.
"""
from django.conf import settings
from django.db import models

from project_management.models import Project, TaskType


class TimeEntry(models.Model):
    """
    A single time entry (timer run). At most one per user has ended_at=None (active timer).
    All database access for time entries goes through TimerService.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="time_entries",
    )
    project = models.ForeignKey(
        Project,
        on_delete=models.PROTECT,
        related_name="time_entries",
    )
    task_type = models.ForeignKey(
        TaskType,
        on_delete=models.PROTECT,
        related_name="time_entries",
    )
    started_at = models.DateTimeField()
    ended_at = models.DateTimeField(null=True, blank=True)
    # Optional override for manual entries (started_at/ended_at may be same-day midnight).
    manual_duration_seconds = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        ordering = ["-started_at"]
        verbose_name_plural = "Time entries"

    def __str__(self):
        return f"{self.user} @ {self.started_at}"

    @property
    def is_active(self):
        return self.ended_at is None

    @property
    def duration_seconds(self):
        """Effective duration: manual override if set, else computed from started_at/ended_at."""
        if self.manual_duration_seconds is not None:
            return self.manual_duration_seconds
        if self.ended_at is None:
            return None
        delta = self.ended_at - self.started_at
        return int(delta.total_seconds())


class TimerAction(models.Model):
    """
    Event-sourced log of timer start/stop actions. Append-only: insert only;
    never update or delete from application code.
    One row per start or stop event.
    """

    class Action(models.TextChoices):
        START = "start", "Start"
        STOP = "stop", "Stop"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="timer_actions",
    )
    action = models.CharField(max_length=10, choices=Action.choices)
    occurred_at = models.DateTimeField()
    time_entry = models.ForeignKey(
        TimeEntry,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="timer_actions",
    )
    project = models.ForeignKey(
        Project,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="timer_actions",
    )
    task_type = models.ForeignKey(
        TaskType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="timer_actions",
    )

    class Meta:
        ordering = ["-occurred_at"]
        verbose_name = "Timer action"
        verbose_name_plural = "Timer actions"

    def __str__(self):
        return f"{self.user_id} {self.action} @ {self.occurred_at}"
