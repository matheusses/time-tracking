"""
TimeEntryRepository: all TimeEntry persistence and queries.
Uses Django ORM; translates to/from domain types. No business rules.
"""
from datetime import timedelta

from tracking.domain.models import ActiveTimerState
from tracking.domain.repositories.time_entry import (
    EntryForWeek,
    TimeEntryRepositoryProtocol,
    TimeEntrySummary,
)
from tracking.models import TimeEntry


def _entry_to_active_state(entry: TimeEntry) -> ActiveTimerState:
    """Build ActiveTimerState from ORM instance."""
    return ActiveTimerState(
        entry_id=entry.id,
        project_id=entry.project_id,
        project_name=entry.project.name if entry.project else None,
        task_type_id=entry.task_type_id,
        task_type_name=entry.task_type.name if entry.task_type else None,
        started_at=entry.started_at,
    )


def _duration_seconds(entry: TimeEntry) -> int:
    """Effective duration in seconds for an entry."""
    if entry.manual_duration_seconds is not None:
        return entry.manual_duration_seconds
    if entry.ended_at is None:
        return 0
    return int((entry.ended_at - entry.started_at).total_seconds())


class TimeEntryRepository(TimeEntryRepositoryProtocol):
    """Django ORM implementation of TimeEntry persistence."""

    def stop_all_active(self, user_id: int, ended_at) -> None:
        TimeEntry.objects.filter(user_id=user_id, ended_at__isnull=True).update(
            ended_at=ended_at
        )

    def create(
        self,
        user_id: int,
        project_id: int,
        task_type_id: int,
        started_at,
        ended_at=None,
    ) -> ActiveTimerState:
        entry = TimeEntry.objects.create(
            user_id=user_id,
            project_id=project_id,
            task_type_id=task_type_id,
            started_at=started_at,
            ended_at=ended_at,
        )
        entry = (
            TimeEntry.objects.filter(pk=entry.pk)
            .select_related("project", "task_type")
            .get()
        )
        return _entry_to_active_state(entry)

    def get_active(self, user_id: int) -> ActiveTimerState | None:
        entry = (
            TimeEntry.objects.filter(user_id=user_id, ended_at__isnull=True)
            .select_related("project", "task_type")
            .first()
        )
        return _entry_to_active_state(entry) if entry else None

    def set_ended_at(self, entry_id: int, ended_at) -> None:
        TimeEntry.objects.filter(pk=entry_id).update(ended_at=ended_at)

    def get_entries_for_week(
        self,
        user_id: int,
        week_start,
        week_end,
    ) -> list[EntryForWeek]:
        entries = (
            TimeEntry.objects.filter(
                user_id=user_id,
                started_at__date__gte=week_start,
                started_at__date__lte=week_end,
            )
            .select_related("project", "task_type")
            .order_by("project_id", "task_type_id", "started_at")
        )
        result: list[EntryForWeek] = []
        for entry in entries:
            result.append(
                EntryForWeek(
                    project_id=entry.project_id,
                    task_type_id=entry.task_type_id,
                    project_name=entry.project.name if entry.project else None,
                    task_type_name=entry.task_type.name if entry.task_type else None,
                    started_at_date=entry.started_at.date(),
                    duration_seconds=_duration_seconds(entry),
                )
            )
        return result

    def has_entries_in_week(self, user_id: int, week_start) -> bool:
        week_end = week_start + timedelta(days=6)
        return TimeEntry.objects.filter(
            user_id=user_id,
            started_at__date__gte=week_start,
            started_at__date__lte=week_end,
        ).exists()

    def delete_completed_for_cell(
        self,
        user_id: int,
        project_id: int | None,
        task_type_id: int | None,
        entry_date,
    ) -> None:
        TimeEntry.objects.filter(
            user_id=user_id,
            project_id=project_id,
            task_type_id=task_type_id,
            started_at__date=entry_date,
            ended_at__isnull=False,
        ).delete()

    def create_manual_entry(
        self,
        user_id: int,
        project_id: int | None,
        task_type_id: int | None,
        started_at,
        ended_at,
        manual_duration_seconds: int,
    ) -> TimeEntrySummary:
        entry = TimeEntry.objects.create(
            user_id=user_id,
            project_id=project_id or None,
            task_type_id=task_type_id or None,
            started_at=started_at,
            ended_at=ended_at,
            manual_duration_seconds=manual_duration_seconds,
        )
        return TimeEntrySummary(
            id=entry.id,
            user_id=entry.user_id,
            project_id=entry.project_id,
            task_type_id=entry.task_type_id,
            entry_date=started_at.date(),
            manual_duration_seconds=manual_duration_seconds,
        )
