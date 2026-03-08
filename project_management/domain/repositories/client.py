"""Client repository protocol. Returns data needed to build DTOs (no ORM in interface)."""
from typing import Protocol

# (id, name) for each client
ClientRow = tuple[int, str]


class ClientRepositoryProtocol(Protocol):
    """Repository for Client domain entity."""

    def list_all(self) -> list[ClientRow]:
        """Return all clients ordered by name. Each item is (id, name)."""
        ...

    def list_by_id(self, client_id: int) -> list[ClientRow]:
        """Return the client with the given id if it exists. At most one row."""
        ...
