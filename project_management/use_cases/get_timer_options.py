"""
GetTimerOptionsUseCase: return projects and task types for the timer form.
Scoped by user's client for non-staff.
"""
from project_management.application.dtos import TimerOptionsDTO
from project_management.use_cases.list_projects import execute as list_projects
from project_management.use_cases.list_task_types import execute as list_task_types


def execute(user_id: int, is_staff: bool = False) -> TimerOptionsDTO:
    """Return project and task type options for the timer dropdowns."""
    projects = list_projects(user_id=user_id, is_staff=is_staff)
    task_types = list_task_types()
    return TimerOptionsDTO(projects=projects, task_types=task_types)
