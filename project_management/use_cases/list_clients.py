"""
ListClientsUseCase: list clients for dropdown/options, scoped by user.
Staff see all; non-staff see only their associated client.
"""
from typing import List

from project_management.application.dtos import ClientOptionDTO
from project_management.domain.services.project_service import ProjectService


def execute(user_id: int, is_staff: bool = False) -> List[ClientOptionDTO]:
    """Return client options for the user (scoped by user's client if non-staff)."""
    service = ProjectService()
    rows = service.list_clients_for_user(user_id=user_id, is_staff=is_staff)
    return [ClientOptionDTO(id=r[0], name=r[1]) for r in rows]
