"""
Django Admin for project_management: Client, Project, Task Type, UserProfile.
Admin-only CRUD; non-admin users do not have access to these management UIs.
"""
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from project_management.models import Client, Project, TaskType, UserProfile

User = get_user_model()


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ("name", "created_at")
    search_fields = ("name",)


class ProjectInline(admin.TabularInline):
    model = Project
    extra = 0
    ordering = ("name",)


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("name", "client", "created_at")
    list_filter = ("client",)
    search_fields = ("name", "client__name")
    inlines = []  # optional: show projects under client


@admin.register(TaskType)
class TaskTypeAdmin(admin.ModelAdmin):
    list_display = ("name", "created_at")
    search_fields = ("name",)


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = True
    verbose_name = "Client association"
    verbose_name_plural = "Client association (project_management)"
    fk_name = "user"


# Extend the default User admin with UserProfile inline so admin can assign users to a client
class UserAdminWithProfile(BaseUserAdmin):
    inlines = (UserProfileInline,)


# Re-register User with our admin so admin can assign client on the user form
if User in admin.site._registry:
    admin.site.unregister(User)
admin.site.register(User, UserAdminWithProfile)
