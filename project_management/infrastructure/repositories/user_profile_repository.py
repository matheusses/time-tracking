"""UserProfileRepository: Django ORM implementation."""
from typing import Optional

from project_management.domain.models import UserProfile


class UserProfileRepository:
    """Django ORM implementation of UserProfileRepositoryProtocol."""

    def get_client_id(self, user_id: int) -> Optional[int]:
        try:
            profile = UserProfile.objects.get(user_id=user_id)
            return profile.client_id if profile.client_id else None
        except UserProfile.DoesNotExist:
            return None
