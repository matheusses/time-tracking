"""ProjectRepository: Django ORM implementation."""
from project_management.domain.models import Project


class ProjectRepository:
    """Django ORM implementation of ProjectRepositoryProtocol."""

    def list_all(self) -> list[tuple[int, str, int]]:
        return list(
            Project.objects.select_related("client")
            .order_by("name")
            .values_list("id", "name", "client_id")
        )

    def list_by_client_id(self, client_id: int) -> list[tuple[int, str, int]]:
        return list(
            Project.objects.filter(client_id=client_id)
            .order_by("name")
            .values_list("id", "name", "client_id")
        )

    def exists(self, project_id: int) -> bool:
        return Project.objects.filter(pk=project_id).exists()
