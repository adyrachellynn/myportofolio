"""Shared Education permissions for views and template controls."""

from rest_framework.permissions import BasePermission, SAFE_METHODS


def can_edit_education(user):
    return user.is_authenticated and (
        user.is_superuser or user.groups.filter(name="Editor").exists()
    )


class IsEducationManagerOrReadOnly(BasePermission):
    """Allow public reads, Editor updates, and superuser management."""

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        if not request.user.is_authenticated:
            return False
        if request.method in ("PUT", "PATCH"):
            return can_edit_education(request.user)
        if request.method in ("POST", "DELETE"):
            return request.user.is_superuser
        return False
