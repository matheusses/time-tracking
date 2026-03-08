"""
StopTimerUseCase: orchestrates stopping the active timer via TimerService.
No direct ORM access; calls TimerService only.
"""
from tracking.application.dtos import StopTimerInputDTO
from tracking.domain.models import TimerResult
from tracking.domain.services.timer_service import TimerService


def execute(dto: StopTimerInputDTO) -> TimerResult:
    """
    Stop the active timer for the user, if any.
    """
    service = TimerService()
    return service.stop(user_id=dto.user_id)
