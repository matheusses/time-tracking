"""
Repository interfaces for project_management domain.
Services depend on these abstractions; implementations live in infrastructure.
"""
from project_management.domain.repositories.client import ClientRepositoryProtocol
from project_management.domain.repositories.project import ProjectRepositoryProtocol
from project_management.domain.repositories.task_type import TaskTypeRepositoryProtocol
from project_management.domain.repositories.user_profile import UserProfileRepositoryProtocol

__all__ = [
    "ClientRepositoryProtocol",
    "ProjectRepositoryProtocol",
    "TaskTypeRepositoryProtocol",
    "UserProfileRepositoryProtocol",
]
