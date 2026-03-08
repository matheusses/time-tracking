"""
Repository interfaces for tracking domain.
Services depend on these abstractions; implementations live in infrastructure.
"""
from tracking.domain.repositories.time_entry import TimeEntryRepositoryProtocol

__all__ = ["TimeEntryRepositoryProtocol"]
