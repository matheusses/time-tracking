"""
TimerService: timer start/stop business logic.
DTO in, DTO out. All persistence via TimeEntryRepository (no ORM in service).
"""
from datetime import timezone
from typing import Optional

from django.utils import timezone as django_tz

from tracking.domain.models import ActiveTimerState, TimerResult
from tracking.domain.repositories import TimeEntryRepositoryProtocol
from tracking.infrastructure.repositories import TimeEntryRepository


class TimerService:
    """
    Domain service for starting and stopping timers.
    Depends on TimeEntryRepository for persistence; returns domain value objects (TimerResult).
    """

    def __init__(
        self,
        time_entry_repository: Optional[TimeEntryRepositoryProtocol] = None,
    ):
        self._repo = time_entry_repository if time_entry_repository is not None else TimeEntryRepository()

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

        self._repo.stop_all_active(user_id=user_id, ended_at=now)
        active = self._repo.create(
            user_id=user_id,
            project_id=project_id or None,
            task_type_id=task_type_id or None,
            started_at=now,
            ended_at=None,
        )
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

        active = self._repo.get_active(user_id=user_id)
        if not active:
            return TimerResult(
                success=False,
                message="No active timer to stop.",
                active_timer=None,
            )

        duration_seconds = int((now - active.started_at).total_seconds())
        self._repo.set_ended_at(entry_id=active.entry_id, ended_at=now)
        entry_id = active.entry_id

        next_active = self._repo.get_active(user_id=user_id)
        return TimerResult(
            success=True,
            message="Timer stopped.",
            active_timer=next_active,
            stopped_entry_id=entry_id,
            stopped_duration_seconds=duration_seconds,
        )

    def get_active_timer(self, user_id: int) -> Optional[ActiveTimerState]:
        """Return the current active timer for the user, or None."""
        return self._repo.get_active(user_id=user_id)
