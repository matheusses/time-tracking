"""TaskTypeRepository: Django ORM implementation."""
from project_management.domain.models import TaskType


class TaskTypeRepository:
    """Django ORM implementation of TaskTypeRepositoryProtocol."""

    def list_all(self) -> list[tuple[int, str]]:
        return list(TaskType.objects.all().order_by("name").values_list("id", "name"))

    def exists(self, task_type_id: int) -> bool:
        return TaskType.objects.filter(pk=task_type_id).exists()
