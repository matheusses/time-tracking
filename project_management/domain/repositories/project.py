"""Project repository protocol. Returns data needed to build DTOs (no ORM in interface)."""
from typing import Optional, Protocol

# (id, name, client_id) for each project
ProjectRow = tuple[int, str, int]


class ProjectRepositoryProtocol(Protocol):
    """Repository for Project domain entity."""

    def list_all(self) -> list[ProjectRow]:
        """Return all projects with (id, name, client_id), ordered by name."""
        ...

    def list_by_client_id(self, client_id: int) -> list[ProjectRow]:
        """Return projects for the given client, ordered by name."""
        ...

    def exists(self, project_id: int) -> bool:
        """Return True if a project with the given id exists."""
        ...
