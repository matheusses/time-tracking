"""
ListProjectsUseCase: list projects for dropdown/options, scoped by user's client.
"""
from typing import List, Optional

from project_management.application.dtos import ProjectOptionDTO
from project_management.domain.services.project_service import ProjectService


def execute(
    user_id: int,
    is_staff: bool = False,
    client_id: Optional[int] = None,
) -> List[ProjectOptionDTO]:
    """Return project options for the user (scoped by user's client if non-staff)."""
    service = ProjectService()
    projects = service.list_projects_for_user(
        user_id=user_id,
        is_staff=is_staff,
        client_id=client_id,
    )
    return [
        ProjectOptionDTO(id=p.id, name=p.name, client_id=p.client_id)
        for p in projects
    ]
