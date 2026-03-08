"""
Shared client instances for all tracking views.
Resolved once at first import; same instances used everywhere (DI singletons).
"""
from core.di import get_project_management_client, get_track_client

track_client = get_track_client()
pm_client = get_project_management_client()
