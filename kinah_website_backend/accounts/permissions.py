from rest_framework import permissions
from django.contrib.contenttypes.models import ContentType


class IsAdminUser(permissions.BasePermission):
    """
    Permission check for admin users
    """
    message = "You must be an admin to perform this action."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Superusers always have permission
        if request.user.is_superuser:
            return True
        
        # Check if user has admin role
        if hasattr(request.user, 'role') and request.user.role:
            return request.user.role.is_admin
        
        return False


class RoleBasedPermission(permissions.BasePermission):
    """
    Advanced role-based permission that checks RolePermission model
    """
    message = "You don't have permission to perform this action."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        # Superusers always have permission
        if request.user.is_superuser:
            return True

        # Admin role users have all permissions
        if hasattr(request.user, 'role') and request.user.role and request.user.role.is_admin:
            return True

        # Get the model being accessed
        model_name = self._get_model_name(view)
        if not model_name:
            return True  # If we can't determine model, allow (fail open for safety)

        # Get content type for the model
        try:
            content_type = ContentType.objects.get(model=model_name.lower())
        except ContentType.DoesNotExist:
            return True  # If content type doesn't exist, allow

        # Check user's role permissions
        if not hasattr(request.user, 'role') or not request.user.role:
            return False

        from .models import RolePermission
        try:
            role_perm = RolePermission.objects.get(
                role=request.user.role,
                content_type=content_type
            )
        except RolePermission.DoesNotExist:
            return False

        # Map HTTP methods to permission fields
        action_map = {
            'GET': 'can_read',
            'POST': 'can_create',
            'PUT': 'can_update',
            'PATCH': 'can_update',
            'DELETE': 'can_delete',
        }

        action_perm = action_map.get(request.method, 'can_read')
        return getattr(role_perm, action_perm, False)

    def _get_model_name(self, view):
        """Extract model name from view"""
        if hasattr(view, 'queryset') and view.queryset is not None:
            return view.queryset.model.__name__
        if hasattr(view, 'model'):
            return view.model.__name__
        return None


class CanCreateAccount(permissions.BasePermission):
    """
    Permission to check if user can create accounts
    """
    message = "You don't have permission to create accounts."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        if request.user.is_superuser:
            return True

        if hasattr(request.user, 'role') and request.user.role and request.user.role.is_admin:
            return True

        # Check specific permission
        if hasattr(request.user, 'role') and request.user.role:
            from .models import RolePermission
            try:
                content_type = ContentType.objects.get_for_model(request.user.__class__)
                role_perm = RolePermission.objects.get(
                    role=request.user.role,
                    content_type=content_type
                )
                return role_perm.can_create_account
            except (RolePermission.DoesNotExist, ContentType.DoesNotExist):
                return False

        return False


class CanDispatchDriver(permissions.BasePermission):
    """
    Permission to check if user can dispatch drivers
    """
    message = "You don't have permission to dispatch drivers."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        if request.user.is_superuser:
            return True

        if hasattr(request.user, 'role') and request.user.role:
            from .models import RolePermission
            try:
                # Get content type for delivery/dispatch model
                content_type = ContentType.objects.get(app_label='parcels', model='delivery')
                role_perm = RolePermission.objects.get(
                    role=request.user.role,
                    content_type=content_type
                )
                return role_perm.can_dispatch_driver
            except (RolePermission.DoesNotExist, ContentType.DoesNotExist):
                return False

        return False


class CanManageResource(permissions.BasePermission):
    """
    Permission to check if user can fully manage a resource
    """
    message = "You don't have permission to manage this resource."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        if request.user.is_superuser:
            return True

        if hasattr(request.user, 'role') and request.user.role and request.user.role.is_admin:
            return True

        # Check manage permission
        model_name = self._get_model_name(view)
        if not model_name:
            return False

        try:
            content_type = ContentType.objects.get(model=model_name.lower())
            from .models import RolePermission
            role_perm = RolePermission.objects.get(
                role=request.user.role,
                content_type=content_type
            )
            return role_perm.can_manage
        except (RolePermission.DoesNotExist, ContentType.DoesNotExist):
            return False

    def _get_model_name(self, view):
        if hasattr(view, 'queryset') and view.queryset is not None:
            return view.queryset.model.__name__
        if hasattr(view, 'model'):
            return view.model.__name__
        return None