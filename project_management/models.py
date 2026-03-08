"""
Django ORM models for project_management app.
Defined in domain.models; re-exported here so Django's app registry and migrations find them.
"""
from project_management.domain.models import Client, Project, TaskType, UserProfile

__all__ = ["Client", "Project", "TaskType", "UserProfile"]
