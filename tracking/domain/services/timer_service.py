"""
TimerService: timer start/stop business logic.
DTO in, DTO out. All persistence via TimeEntryRepository and TimerActionRepository (no ORM in service).
Validation of project/task_type uses the upstream client contract (no cross-module repository calls).
"""
from __future__ import annotations

from datetime import timezone
from typing import Optional, Protocol

from django.utils import timezone as django_tz

from tracking.domain.models import ActiveTimerState, TimerResult
from tracking.domain.repositories import TimeEntryRepositoryProtocol, TimerActionRepositoryProtocol
from tracking.infrastructure.repositories import TimeEntryRepository, TimerActionRepository


class TimerValidationError(ValueError):
    """Raised when start_timer validation fails (missing or invalid project_id, task_type_id)."""

    def __init__(self, message: str, code: str = "invalid_input"):
        self.message = message
        self.code = code
        super().__init__(message)


class ProjectTaskTypeValidatorProtocol(Protocol):
    """
    Contract for validating project and task type existence.
    Implemented by the upstream (project_management) client; tracking uses this interface only.
    """

    def project_exists(self, project_id: int) -> bool:
        """Return True if the project exists."""
        ...

    def task_type_exists(self, task_type_id: int) -> bool:
        """Return True if the task type exists."""
        ...


class TimerService:
    """
    Domain service for starting and stopping timers.
    Depends on TimeEntryRepository, TimerActionRepository (append-only), and optionally
    a client that implements ProjectTaskTypeValidatorProtocol for validation.
    Does not depend on repositories from other modules.
    """

    def __init__(
        self,
        time_entry_repository: Optional[TimeEntryRepositoryProtocol] = None,
        timer_action_repository: Optional[TimerActionRepositoryProtocol] = None,
        project_task_type_validator: Optional[ProjectTaskTypeValidatorProtocol] = None,
    ):
        self._repo = (
            time_entry_repository
            if time_entry_repository is not None
            else TimeEntryRepository()
        )
        self._action_repo = (
            timer_action_repository
            if timer_action_repository is not None
            else TimerActionRepository()
        )
        self._validator = project_task_type_validator

    def start(
        self,
        user_id: int,
        project_id: Optional[int] = None,
        task_type_id: Optional[int] = None,
    ) -> TimerResult:
        """
        Start a new timer for the user. Requires project_id and task_type_id (valid and existing).
        Stops any existing active timer first (single active timer per user).
        Creates a new TimeEntry and appends a start event to the action log.
        """
        if project_id is None:
            raise TimerValidationError("Project is required.", code="missing_project")
        if task_type_id is None:
            raise TimerValidationError("Task type is required.", code="missing_task_type")
        if self._validator is not None:
            if not self._validator.project_exists(project_id):
                raise TimerValidationError("Invalid project.", code="invalid_project")
            if not self._validator.task_type_exists(task_type_id):
                raise TimerValidationError("Invalid task type.", code="invalid_task_type")

        now = django_tz.now()
        if now.tzinfo is None:
            now = now.replace(tzinfo=timezone.utc)

        self._repo.stop_all_active(user_id=user_id, ended_at=now)
        active = self._repo.create(
            user_id=user_id,
            project_id=project_id,
            task_type_id=task_type_id,
            started_at=now,
            ended_at=None,
        )
        # Always set time_entry_id so tracking_timeraction links to the created TimeEntry
        entry_id = active.entry_id
        self._action_repo.append(
            user_id=user_id,
            action="start",
            occurred_at=now,
            time_entry_id=entry_id,
            project_id=project_id,
            task_type_id=task_type_id,
        )
        return TimerResult(
            success=True,
            message="Timer started.",
            active_timer=active,
        )

    def stop(self, user_id: int) -> TimerResult:
        """
        Stop the active timer for the user (if any). Sets ended_at to now,
        appends a stop event to the action log, and returns the stopped entry info.
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
        entry_id = active.entry_id
        self._repo.set_ended_at(entry_id=entry_id, ended_at=now)

        # Always set time_entry_id so tracking_timeraction links to the stopped TimeEntry
        self._action_repo.append(
            user_id=user_id,
            action="stop",
            occurred_at=now,
            time_entry_id=entry_id,
            project_id=active.project_id,
            task_type_id=active.task_type_id,
        )

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
