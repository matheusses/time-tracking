"""
TimerService: all timer-related database operations.
Enforces single active timer per user (stop existing before start).
"""
from datetime import timezone
from typing import Optional

from django.utils import timezone as django_tz

from tracking.domain.models import ActiveTimerState, TimerResult
from tracking.models import TimeEntry


class TimerService:
    """
    Domain service for starting and stopping timers.
    All ORM access for time entries is centralized here.
    """

    def start(
        self,
        user_id: int,
        project_id: Optional[int] = None,
        task_type_id: Optional[int] = None,
    ) -> TimerResult:
        """
        Start a new timer for the user. Stops any existing active timer first
        (single active timer per user). Creates a new TimeEntry with ended_at=None.
        """
        now = django_tz.now()
        if now.tzinfo is None:
            now = now.replace(tzinfo=timezone.utc)

        # Stop any existing active timer for this user
        TimeEntry.objects.filter(user_id=user_id, ended_at__isnull=True).update(
            ended_at=now
        )

        entry = TimeEntry.objects.create(
            user_id=user_id,
            project_id=project_id or None,
            task_type_id=task_type_id or None,
            started_at=now,
            ended_at=None,
        )

        active = self._entry_to_active_state(entry)
        return TimerResult(
            success=True,
            message="Timer started.",
            active_timer=active,
        )

    def stop(self, user_id: int) -> TimerResult:
        """
        Stop the active timer for the user (if any). Sets ended_at to now
        and returns the stopped entry info.
        """
        now = django_tz.now()
        if now.tzinfo is None:
            now = now.replace(tzinfo=timezone.utc)

        active = TimeEntry.objects.filter(
            user_id=user_id, ended_at__isnull=True
        ).select_related("project", "task_type").first()

        if not active:
            return TimerResult(
                success=False,
                message="No active timer to stop.",
                active_timer=None,
            )

        duration_seconds = int((now - active.started_at).total_seconds())
        active.ended_at = now
        active.save(update_fields=["ended_at"])
        entry_id = active.id

        # Check if user has another active timer (should not happen)
        next_active = TimeEntry.objects.filter(
            user_id=user_id, ended_at__isnull=True
        ).select_related("project", "task_type").first()

        return TimerResult(
            success=True,
            message="Timer stopped.",
            active_timer=self._entry_to_active_state(next_active) if next_active else None,
            stopped_entry_id=entry_id,
            stopped_duration_seconds=duration_seconds,
        )

    def get_active_timer(self, user_id: int) -> Optional[ActiveTimerState]:
        """Return the current active timer for the user, or None."""
        entry = (
            TimeEntry.objects.filter(user_id=user_id, ended_at__isnull=True)
            .select_related("project", "task_type")
            .first()
        )
        return self._entry_to_active_state(entry) if entry else None

    @staticmethod
    def _entry_to_active_state(entry: Optional[TimeEntry]) -> Optional[ActiveTimerState]:
        if entry is None:
            return None
        return ActiveTimerState(
            entry_id=entry.id,
            project_id=entry.project_id,
            project_name=entry.project.name if entry.project else None,
            task_type_id=entry.task_type_id,
            task_type_name=entry.task_type.name if entry.task_type else None,
            started_at=entry.started_at,
        )
