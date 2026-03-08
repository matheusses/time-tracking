"""
ProjectService: all DB access for clients, projects, and task types.
Used by admin (via ORM or this layer) and by list use cases for dropdown options.
Non-admin lists are scoped by the user's associated client (UserProfile).
"""
from typing import List, Optional

from project_management.domain.models import Client, Project, TaskType, UserProfile


class ProjectService:
    """
    Domain service for client, project, and task type data.
    All ORM access for these entities is centralized here.
    """

    def get_user_client_id(self, user_id: int) -> Optional[int]:
        """Return the client_id for the user's profile, or None if unset or no profile."""
        try:
            profile = UserProfile.objects.get(user_id=user_id)
            return profile.client_id if profile.client_id else None
        except UserProfile.DoesNotExist:
            return None

    def list_clients_for_user(
        self,
        user_id: int,
        is_staff: bool = False,
    ) -> List[Client]:
        """
        List clients available to the user for dropdowns.
        Staff: all clients. Non-staff: only the user's associated client (if any).
        """
        if is_staff:
            return list(Client.objects.all().order_by("name"))
        client_id = self.get_user_client_id(user_id)
        if client_id is None:
            return []
        return list(Client.objects.filter(pk=client_id).order_by("name"))

    def list_projects_for_user(
        self,
        user_id: int,
        is_staff: bool = False,
        client_id: Optional[int] = None,
    ) -> List[Project]:
        """
        List projects available to the user for dropdowns.
        Non-staff: only projects for the user's associated client.
        Staff: all projects, or filtered by client_id if given.
        """
        if is_staff and client_id is None:
            return list(Project.objects.select_related("client").order_by("name"))
        if is_staff and client_id is not None:
            return list(
                Project.objects.filter(client_id=client_id)
                .select_related("client")
                .order_by("name")
            )
        # Non-staff: scope by user's client
        user_client_id = self.get_user_client_id(user_id)
        if user_client_id is None:
            return []
        return list(
            Project.objects.filter(client_id=user_client_id)
            .select_related("client")
            .order_by("name")
        )

    def list_task_types(self) -> List[TaskType]:
        """List all task types (e.g. for dropdowns). Task types are global."""
        return list(TaskType.objects.all().order_by("name"))
