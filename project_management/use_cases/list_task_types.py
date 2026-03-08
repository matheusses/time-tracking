"""
ListTaskTypesUseCase: list task types for dropdown/options.
Task types are global (no client scope).
"""
from typing import List

from project_management.application.dtos import TaskTypeOptionDTO
from project_management.domain.services.project_service import ProjectService


def execute() -> List[TaskTypeOptionDTO]:
    """Return all task type options."""
    service = ProjectService()
    rows = service.list_task_types()
    return [TaskTypeOptionDTO(id=r[0], name=r[1]) for r in rows]
