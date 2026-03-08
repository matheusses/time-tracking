"""
Domain models: state and invariants only.
No database operations; ORM lives in domain services.
"""
from tracking.domain.models.timer import ActiveTimerState, TimerResult

__all__ = ["ActiveTimerState", "TimerResult"]
