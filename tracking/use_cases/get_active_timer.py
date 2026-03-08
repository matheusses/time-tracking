"""
GetActiveTimerUseCase: returns the current active timer for the user, if any.
Used by the timer partial view to render current state (no start/stop).
"""
from typing import Optional

from tracking.domain.models import ActiveTimerState
from tracking.domain.services.timer_service import TimerService


def execute(user_id: int) -> Optional[ActiveTimerState]:
    """Return the active timer for the user, or None."""
    service = TimerService()
    return service.get_active_timer(user_id)
