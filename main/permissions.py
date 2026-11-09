"""Shared role permissions for portfolio views and API endpoints."""

from rest_framework.permissions import BasePermission, SAFE_METHODS


def can_edit_education(user):
    return user.is_authenticated and (
        user.is_superuser or user.groups.filter(name="Editor").exists()
    )


def can_edit_project(user):
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


class IsPortfolioOwnerOrEditorOrReadOnly(BasePermission):
    """
    Allow public reads, Editor/superuser updates,
    and superuser create/delete for Project.
    """

    message = "You do not have permission to modify this project."

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True

        if not request.user.is_authenticated:
            return False

        if request.method in ("PUT", "PATCH"):
            return can_edit_project(request.user)

        if request.method in ("POST", "DELETE"):
            return request.user.is_superuser

        return False


class IsPortfolioOwnerOrReadOnly(IsPortfolioOwnerOrEditorOrReadOnly):
    """
    Alias sementara agar import lama tidak rusak.
    Nanti api_views.py akan memakai nama permission baru.
    """

    pass