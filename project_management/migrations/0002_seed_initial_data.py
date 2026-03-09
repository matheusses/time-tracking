from django.contrib.auth.hashers import make_password
from django.db import migrations


def seed_initial_data(apps, schema_editor):
    User = apps.get_model("auth", "User")
    Client = apps.get_model("project_management", "Client")
    UserProfile = apps.get_model("project_management", "UserProfile")
    Project = apps.get_model("project_management", "Project")
    TaskType = apps.get_model("project_management", "TaskType")

    # 1. Create client if not exists
    client, _ = Client.objects.get_or_create(name="Client Joe")

    # 2. Create admin user (John Doe - Admin) and associate with client
    admin_user, _ = User.objects.get_or_create(
        username="john_doe_admin",
        defaults={
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe.admin@example.com",
            "is_staff": True,
            "is_superuser": True,
            "password": make_password("changeme"),
        },
    )
    UserProfile.objects.get_or_create(user=admin_user, defaults={"client": client})

    # 3. Create regular user (John Doe) and associate with client
    regular_user, _ = User.objects.get_or_create(
        username="john_doe",
        defaults={
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@example.com",
            "is_staff": False,
            "is_superuser": False,
            "password": make_password("changeme"),
        },
    )
    UserProfile.objects.get_or_create(user=regular_user, defaults={"client": client})

    # 4. Create project associated with the client
    Project.objects.get_or_create(name="Project X", client=client)

    # 5. Create task types (Design, Development, Meeting)
    for task_name in ["Design", "Development", "Meeting"]:
        TaskType.objects.get_or_create(name=task_name)


def reverse_seed(apps, schema_editor):
    pass  # noop — seed data is not removed on rollback


class Migration(migrations.Migration):

    dependencies = [
        ("project_management", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed_initial_data, reverse_seed),
    ]
