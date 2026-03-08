"""
Dependency injection container.
Provides repository and client instances. All layers communicate via interfaces;
only this module wires concrete implementations.
"""
from typing import Optional

from project_management.domain.repositories import (
    ClientRepositoryProtocol,
    ProjectRepositoryProtocol,
    TaskTypeRepositoryProtocol,
    UserProfileRepositoryProtocol,
)
from project_management.infrastructure.repositories import (
    ClientRepository,
    ProjectRepository,
    TaskTypeRepository,
    UserProfileRepository,
)
from tracking.domain.repositories import TimeEntryRepositoryProtocol, TimerActionRepositoryProtocol
from tracking.infrastructure.repositories import TimeEntryRepository, TimerActionRepository


class DI:
    """
    DI container: creates and holds repository and client dependencies.
    Use get_* methods to obtain instances. Repositories are created once per container.
    """

    def __init__(self) -> None:
        self._time_entry_repository: Optional[TimeEntryRepositoryProtocol] = None
        self._timer_action_repository: Optional[TimerActionRepositoryProtocol] = None
        self._project_repository: Optional[ProjectRepositoryProtocol] = None
        self._task_type_repository: Optional[TaskTypeRepositoryProtocol] = None
        self._client_repository: Optional[ClientRepositoryProtocol] = None
        self._user_profile_repository: Optional[UserProfileRepositoryProtocol] = None
        self._track_client = None
        self._project_management_client = None

    def get_time_entry_repository(self) -> TimeEntryRepositoryProtocol:
        """Return the TimeEntry repository implementation."""
        if self._time_entry_repository is None:
            self._time_entry_repository = TimeEntryRepository()
        return self._time_entry_repository

    def get_timer_action_repository(self) -> TimerActionRepositoryProtocol:
        """Return the TimerAction repository implementation (insert-only)."""
        if self._timer_action_repository is None:
            self._timer_action_repository = TimerActionRepository()
        return self._timer_action_repository

    def get_project_repository(self) -> ProjectRepositoryProtocol:
        """Return the Project repository implementation."""
        if self._project_repository is None:
            self._project_repository = ProjectRepository()
        return self._project_repository

    def get_task_type_repository(self) -> TaskTypeRepositoryProtocol:
        """Return the TaskType repository implementation."""
        if self._task_type_repository is None:
            self._task_type_repository = TaskTypeRepository()
        return self._task_type_repository

    def get_client_repository(self) -> ClientRepositoryProtocol:
        """Return the Client repository implementation."""
        if self._client_repository is None:
            self._client_repository = ClientRepository()
        return self._client_repository

    def get_user_profile_repository(self) -> UserProfileRepositoryProtocol:
        """Return the UserProfile repository implementation."""
        if self._user_profile_repository is None:
            self._user_profile_repository = UserProfileRepository()
        return self._user_profile_repository

    def get_track_client(self):  # -> TrackClientInterface (forward ref to avoid circular import)
        """Return the Track client (single entry point for tracking use cases)."""
        if self._track_client is None:
            from tracking.application.clients import TrackClient

            self._track_client = TrackClient(
                time_entry_repository=self.get_time_entry_repository(),
                timer_action_repository=self.get_timer_action_repository(),
                project_management_client=self.get_project_management_client(),
            )
        return self._track_client

    def get_project_management_client(self):  # -> ProjectManagementClientInterface
        """Return the ProjectManagement client (single entry point for PM use cases)."""
        if self._project_management_client is None:
            from project_management.application.clients import ProjectManagementClient

            self._project_management_client = ProjectManagementClient(
                user_profile_repository=self.get_user_profile_repository(),
                client_repository=self.get_client_repository(),
                project_repository=self.get_project_repository(),
                task_type_repository=self.get_task_type_repository(),
            )
        return self._project_management_client


# Module-level default container for application use
_default_di: Optional[DI] = None


def get_di() -> DI:
    """Return the default DI container. Creates it on first access."""
    global _default_di
    if _default_di is None:
        _default_di = DI()
    return _default_di


def get_track_client():
    """Return the Track client from the default DI container."""
    return get_di().get_track_client()


def get_project_management_client():
    """Return the ProjectManagement client from the default DI container."""
    return get_di().get_project_management_client()
