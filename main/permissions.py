"""Shared Education permissions for views and template controls."""


def can_edit_education(user):
    return user.is_authenticated and (
        user.is_superuser or user.groups.filter(name="Editor").exists()
    )
