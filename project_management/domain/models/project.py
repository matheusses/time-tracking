"""
Project model. Belongs to a Client (Client > Project hierarchy).
"""
from django.db import models

from project_management.domain.models.client import Client


class Project(models.Model):
    """Project belonging to a client. Time is logged against projects."""

    name = models.CharField(max_length=255)
    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        related_name="projects",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]
        unique_together = [["client", "name"]]

    def __str__(self):
        return self.name
