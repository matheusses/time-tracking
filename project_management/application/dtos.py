"""DTOs for project_management use cases (dropdown options)."""
from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class ClientOptionDTO:
    """Client option for dropdowns."""

    id: int
    name: str


@dataclass(frozen=True)
class ProjectOptionDTO:
    """Project option for dropdowns."""

    id: int
    name: str
    client_id: int


@dataclass(frozen=True)
class TaskTypeOptionDTO:
    """Task type option for dropdowns."""

    id: int
    name: str


@dataclass(frozen=True)
class TimerOptionsDTO:
    """All options needed for the timer form: projects and task types (and optionally clients)."""

    projects: List[ProjectOptionDTO]
    task_types: List[TaskTypeOptionDTO]
