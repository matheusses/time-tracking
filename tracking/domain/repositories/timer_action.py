"""
TimerAction repository protocol. Event-sourced: insert-only (append).
No update or delete methods; this table must never be updated or deleted from application code.
"""
from datetime import datetime
from typing import Optional, Protocol


class TimerActionRepositoryProtocol(Protocol):
    """
    Repository for appending timer action events. Insert-only; no update/delete.
    """

    def append(
        self,
        *,
        user_id: int,
        action: str,
        occurred_at: datetime,
        time_entry_id: Optional[int] = None,
        project_id: Optional[int] = None,
        task_type_id: Optional[int] = None,
        value: Optional[int] = None,
    ) -> None:
        """
        Append one timer action event (start, stop, or manual). No return value.
        value is used for manual actions (duration_seconds). Never updates or deletes existing rows.
        """
        ...
