"""UserProfile repository protocol. Returns simple values (no ORM in interface)."""
from typing import Optional, Protocol


class UserProfileRepositoryProtocol(Protocol):
    """Repository for user–client association. Used to scope client/project options."""

    def get_client_id(self, user_id: int) -> Optional[int]:
        """Return the client_id for the user's profile, or None if unset or no profile."""
        ...
