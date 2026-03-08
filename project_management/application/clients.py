"""
ProjectManagement client: single entry point for project_management use cases.
Views and other modules depend on ProjectManagementClientInterface only.
"""
from typing import List, Optional, Protocol

from project_management.application.dtos import (
    ClientOptionDTO,
    ProjectOptionDTO,
    TaskTypeOptionDTO,
    TimerOptionsDTO,
)
from project_management.domain.repositories import (
    ClientRepositoryProtocol,
    ProjectRepositoryProtocol,
    TaskTypeRepositoryProtocol,
    UserProfileRepositoryProtocol,
)
from project_management.domain.services.project_service import ProjectService


class ProjectManagementClientInterface(Protocol):
    """Protocol for the project_management client. All PM use cases are exposed here."""

    def get_timer_options(
        self, user_id: int, *, is_staff: bool = False
    ) -> TimerOptionsDTO:
        """Return project and task type options for the timer form."""
        ...

    def list_projects(
        self,
        user_id: int,
        *,
        is_staff: bool = False,
        client_id: Optional[int] = None,
    ) -> List[ProjectOptionDTO]:
        """Return project options for the user (scoped by client if non-staff)."""
        ...

    def list_clients(
        self, user_id: int, *, is_staff: bool = False
    ) -> List[ClientOptionDTO]:
        """Return client options for the user (scoped if non-staff)."""
        ...

    def list_task_types(self) -> List[TaskTypeOptionDTO]:
        """Return all task type options."""
        ...


class ProjectManagementClient:
    """
    Client for project_management module. Builds ProjectService from repository
    interfaces and exposes use-case-style methods.
    """

    def __init__(
        self,
        user_profile_repository: UserProfileRepositoryProtocol,
        client_repository: ClientRepositoryProtocol,
        project_repository: ProjectRepositoryProtocol,
        task_type_repository: TaskTypeRepositoryProtocol,
    ) -> None:
        self._project_service = ProjectService(
            user_profile_repository=user_profile_repository,
            client_repository=client_repository,
            project_repository=project_repository,
            task_type_repository=task_type_repository,
        )

    def get_timer_options(
        self, user_id: int, *, is_staff: bool = False
    ) -> TimerOptionsDTO:
        """Return project and task type options for the timer form."""
        projects = self.list_projects(user_id=user_id, is_staff=is_staff)
        task_types = self.list_task_types()
        return TimerOptionsDTO(projects=projects, task_types=task_types)

    def list_projects(
        self,
        user_id: int,
        *,
        is_staff: bool = False,
        client_id: Optional[int] = None,
    ) -> List[ProjectOptionDTO]:
        """Return project options for the user (scoped by client if non-staff)."""
        rows = self._project_service.list_projects_for_user(
            user_id=user_id,
            is_staff=is_staff,
            client_id=client_id,
        )
        return [
            ProjectOptionDTO(id=r[0], name=r[1], client_id=r[2])
            for r in rows
        ]

    def list_clients(
        self, user_id: int, *, is_staff: bool = False
    ) -> List[ClientOptionDTO]:
        """Return client options for the user (scoped if non-staff)."""
        rows = self._project_service.list_clients_for_user(
            user_id=user_id,
            is_staff=is_staff,
        )
        return [ClientOptionDTO(id=r[0], name=r[1]) for r in rows]

    def list_task_types(self) -> List[TaskTypeOptionDTO]:
        """Return all task type options."""
        rows = self._project_service.list_task_types()
        return [TaskTypeOptionDTO(id=r[0], name=r[1]) for r in rows]
