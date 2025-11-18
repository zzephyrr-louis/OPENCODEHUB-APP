from django import template
from accounts.models import SharedProject

register = template.Library()

@register.filter
def has_edit_permission(user, project):
    """Check if user has edit permission on a project"""
    if project.owner == user:
        return True
    
    shared_project = SharedProject.objects.filter(
        project=project,
        user=user,
        permission='edit'
    ).first()
    
    return shared_project is not None

@register.filter
def has_view_permission(user, project):
    """Check if user has at least view permission on a project"""
    if project.owner == user:
        return True
    
    shared_project = SharedProject.objects.filter(
        project=project,
        user=user
    ).first()
    
    return shared_project is not None

@register.filter
def get_user_permission(user, project):
    """Get user's permission level for a project"""
    if project.owner == user:
        return 'owner'
    
    shared_project = SharedProject.objects.filter(
        project=project,
        user=user
    ).first()
    
    if shared_project:
        return shared_project.permission
    
    return None
