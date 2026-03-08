"""
Timer domain models: state and value objects for timer operations.
No database access; used by TimerService and use cases for input/output.
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(frozen=True)
class ActiveTimerState:
    """
    Represents the current active timer for a user (if any).
    Invariant: at most one active timer per user (enforced by TimerService).
    """

    entry_id: int
    project_id: Optional[int]
    project_name: Optional[str]
    task_type_id: Optional[int]
    task_type_name: Optional[str]
    started_at: datetime

    @property
    def duration_seconds(self) -> Optional[int]:
        """None while timer is still running (no end time)."""
        return None


@dataclass(frozen=True)
class TimerResult:
    """Result of a start or stop timer operation."""

    success: bool
    message: str
    active_timer: Optional[ActiveTimerState] = None
    stopped_entry_id: Optional[int] = None
    stopped_duration_seconds: Optional[int] = None
