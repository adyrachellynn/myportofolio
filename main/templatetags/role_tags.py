from django import template

from main.permissions import can_edit_education

register = template.Library()


@register.simple_tag
def navbar_role(user):
    """Display the highest applicable role without granting permissions."""
    if not user.is_authenticated:
        return ""
    if user.is_superuser:
        return "Admin"
    if can_edit_education(user):
        return "Editor"
    return "User"
