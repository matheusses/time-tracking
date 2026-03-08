"""
ProjectService: client, project, and task type listing.
All persistence via repositories (no ORM in service). Returns row data for use cases to build DTOs.
"""
from typing import List, Optional

from project_management.domain.repositories import (
    ClientRepositoryProtocol,
    ProjectRepositoryProtocol,
    TaskTypeRepositoryProtocol,
    UserProfileRepositoryProtocol,
)
from project_management.domain.repositories.client import ClientRow
from project_management.domain.repositories.project import ProjectRow
from project_management.domain.repositories.task_type import TaskTypeRow
from project_management.infrastructure.repositories import (
    ClientRepository,
    ProjectRepository,
    TaskTypeRepository,
    UserProfileRepository,
)


class ProjectService:
    """
    Domain service for client, project, and task type data.
    Depends on repositories; returns row data (id, name, ...) for use cases to build DTOs.
    """

    def __init__(
        self,
        user_profile_repository: Optional[UserProfileRepositoryProtocol] = None,
        client_repository: Optional[ClientRepositoryProtocol] = None,
        project_repository: Optional[ProjectRepositoryProtocol] = None,
        task_type_repository: Optional[TaskTypeRepositoryProtocol] = None,
    ):
        self._user_profile_repo = (
            user_profile_repository if user_profile_repository is not None else UserProfileRepository()
        )
        self._client_repo = (
            client_repository if client_repository is not None else ClientRepository()
        )
        self._project_repo = (
            project_repository if project_repository is not None else ProjectRepository()
        )
        self._task_type_repo = (
            task_type_repository if task_type_repository is not None else TaskTypeRepository()
        )

    def get_user_client_id(self, user_id: int) -> Optional[int]:
        """Return the client_id for the user's profile, or None if unset or no profile."""
        return self._user_profile_repo.get_client_id(user_id=user_id)

    def list_clients_for_user(
        self,
        user_id: int,
        is_staff: bool = False,
    ) -> List[ClientRow]:
        """
        List clients available to the user (as rows: id, name).
        Staff: all clients. Non-staff: only the user's associated client (if any).
        """
        if is_staff:
            return self._client_repo.list_all()
        client_id = self.get_user_client_id(user_id)
        if client_id is None:
            return []
        return self._client_repo.list_by_id(client_id)

    def list_projects_for_user(
        self,
        user_id: int,
        is_staff: bool = False,
        client_id: Optional[int] = None,
    ) -> List[ProjectRow]:
        """
        List projects available to the user (as rows: id, name, client_id).
        Non-staff: only projects for the user's associated client.
        Staff: all projects, or filtered by client_id if given.
        """
        if is_staff and client_id is None:
            return self._project_repo.list_all()
        if is_staff and client_id is not None:
            return self._project_repo.list_by_client_id(client_id)
        user_client_id = self.get_user_client_id(user_id)
        if user_client_id is None:
            return []
        return self._project_repo.list_by_client_id(user_client_id)

    def list_task_types(self) -> List[TaskTypeRow]:
        """List all task types (as rows: id, name). Task types are global."""
        return self._task_type_repo.list_all()
