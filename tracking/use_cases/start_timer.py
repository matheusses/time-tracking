"""
StartTimerUseCase: orchestrates starting a timer via TimerService.
No direct ORM access; calls TimerService only.
"""
from tracking.application.dtos import StartTimerInputDTO
from tracking.domain.models import TimerResult
from tracking.domain.services.timer_service import TimerService


def execute(dto: StartTimerInputDTO) -> TimerResult:
    """
    Start a new timer for the user. Any existing active timer is stopped first.
    """
    service = TimerService()
    return service.start(
        user_id=dto.user_id,
        project_id=dto.project_id,
        task_type_id=dto.task_type_id,
    )
