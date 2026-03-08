"""
User–client association. Admin assigns each user to one client.
Non-admin options (clients/projects/task types) are scoped by this association.
"""
from django.conf import settings
from django.db import models

from project_management.domain.models.client import Client


class UserProfile(models.Model):
    """Links a user to a single client. Used to scope project/task-type options."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="project_management_profile",
    )
    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        related_name="user_profiles",
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = "User profile (client association)"
        verbose_name_plural = "User profiles (client association)"

    def __str__(self):
        return f"{self.user.get_username()} → {self.client.name if self.client else '—'}"
