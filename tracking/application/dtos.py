"""
DTOs for timer use cases. Used by views to pass input and by use cases to return results.
"""
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class StartTimerInputDTO:
    """Input for starting a timer."""

    user_id: int
    project_id: Optional[int] = None
    task_type_id: Optional[int] = None


@dataclass(frozen=True)
class StopTimerInputDTO:
    """Input for stopping the active timer."""

    user_id: int


# Result type: use cases return tracking.domain.models.TimerResult (no separate output DTO).
