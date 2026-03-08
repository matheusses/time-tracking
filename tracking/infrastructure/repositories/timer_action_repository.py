"""
TimerActionRepository: append-only persistence for timer events.
Event-sourced: only insert; no update or delete. This module must never
update or delete TimerAction rows.
"""
from datetime import datetime
from typing import Optional

from tracking.models import TimerAction


class TimerActionRepository:
    """Django ORM implementation. Insert-only (append); no update/delete methods."""

    def append(
        self,
        *,
        user_id: int,
        action: str,
        occurred_at: datetime,
        time_entry_id: Optional[int] = None,
        project_id: Optional[int] = None,
        task_type_id: Optional[int] = None,
    ) -> None:
        """Append one timer action event. Never updates or deletes."""
        TimerAction.objects.create(
            user_id=user_id,
            action=action,
            occurred_at=occurred_at,
            time_entry_id=time_entry_id,
            project_id=project_id,
            task_type_id=task_type_id,
        )
