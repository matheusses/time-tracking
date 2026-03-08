"""
Client model. Top of hierarchy: Client > Project.
Admin creates clients; non-admin options are scoped by user's associated client.
"""
from django.db import models


class Client(models.Model):
    """Client that owns one or more projects."""

    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name
