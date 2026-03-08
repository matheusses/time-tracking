"""TaskType repository protocol. Returns data needed to build DTOs (no ORM in interface)."""
from typing import Protocol

# (id, name) for each task type
TaskTypeRow = tuple[int, str]


class TaskTypeRepositoryProtocol(Protocol):
    """Repository for TaskType domain entity."""

    def list_all(self) -> list[TaskTypeRow]:
        """Return all task types ordered by name."""
        ...

    def exists(self, task_type_id: int) -> bool:
        """Return True if a task type with the given id exists."""
        ...
