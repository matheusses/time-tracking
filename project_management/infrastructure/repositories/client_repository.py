"""ClientRepository: Django ORM implementation."""
from project_management.domain.models import Client


class ClientRepository:
    """Django ORM implementation of ClientRepositoryProtocol."""

    def list_all(self) -> list[tuple[int, str]]:
        return list(Client.objects.all().order_by("name").values_list("id", "name"))

    def list_by_id(self, client_id: int) -> list[tuple[int, str]]:
        qs = Client.objects.filter(pk=client_id).order_by("name").values_list("id", "name")
        return list(qs)
