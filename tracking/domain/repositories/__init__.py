"""
Repository interfaces for tracking domain.
Services depend on these abstractions; implementations live in infrastructure.
"""
from tracking.domain.repositories.time_entry import TimeEntryRepositoryProtocol
from tracking.domain.repositories.timer_action import TimerActionRepositoryProtocol

__all__ = ["TimeEntryRepositoryProtocol", "TimerActionRepositoryProtocol"]
