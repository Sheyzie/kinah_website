from rest_framework import permissions
from django.contrib.contenttypes.models import ContentType
from django.db import transaction


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
    

class IsStaffUser(permissions.BasePermission):
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
        
        # Admin user should have permission
        if hasattr(request.user, 'role') and request.user.role:
            return request.user.role.is_admin
        
        # Check if user has staff role
        if hasattr(request.user, 'role') and request.user.role:
            return request.user.role.role_name == 'staff'
        
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

        # if hasattr(request.user, 'role') and request.user.role and request.user.role.is_admin:
        #     return True

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
    
    
class IsDispatcher(permissions.BasePermission):
    """
    Permission to check if user is a dispatcher
    """
    message = "You don't have permission to manage this resource."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        if request.user.is_superuser:
            return True

        if hasattr(request.user, 'role') and request.user.role and request.user.role.is_admin:
            return True
        
        if hasattr(request.user, 'role') and request.user.role and request.user.role.role_name == 'dispatcher':
            return True
        
        return False
    
    
class IsBuyer(permissions.BasePermission):
    """
    Permission to check if user is a buyer
    """
    message = "You don't have permission to carry out this action."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            # TODO: get tracking details and check in order
            return False

        if request.user.is_superuser:
            return True

        if hasattr(request.user, 'role') and request.user.role and request.user.role.is_admin:
            return True
        
        if hasattr(request.user, 'role') and request.user.role and request.user.role.role_name == 'staff':
            return True
        
        # TODO: get the order obj and check if order.user == user
        
        return False
    

class DefaultPermission:
    '''
    class to set default permissions for default roles
    '''

    def __init__(self, role):
        self.role = role
        self.perms_map = []

    def set_buyer_default_perms(self):
        from .models import RolePermission

        self.perms_map = [
            {
                'model': 'user',
                'app_label': 'accounts',
                'perms': ['can_read', 'can_update', 'can_delete']
            },
            {
                'model': 'address',
                'app_label': 'finance',
                'perms': ['can_read', 'can_update']
            },
            {
                'model': 'order',
                'app_label': 'finance',
                'perms': ['can_read']
            },
            {
                'model': 'review',
                'app_label': 'products',
                'perms': ['can_read', 'can_create', 'can_delete']
            },
            {
                'model': 'product',
                'app_label': 'products',
                'perms': ['can_read']
            },
            {
                'model': 'productstype',
                'app_label': 'products',
                'perms': ['can_read']
            },
            {
                'model': 'productscategory',
                'app_label': 'products',
                'perms': ['can_read']
            },
        ]

        self._create_perms()

    def set_dispatcher_default_perms(self):
        from .models import RolePermission

        self.perms_map = [
            {
                'model': 'user',
                'app_label': 'accounts',
                'perms': ['can_read', 'can_update']
            },
            {
                'model': 'address',
                'app_label': 'finance',
                'perms': ['can_read', 'can_update']
            },
            {
                'model': 'order',
                'app_label': 'finance',
                'perms': ['can_read']
            },
            {
                'model': 'product',
                'app_label': 'products',
                'perms': ['can_read']
            },
            {
                'model': 'productstype',
                'app_label': 'products',
                'perms': ['can_read']
            },
            {
                'model': 'productscategory',
                'app_label': 'products',
                'perms': ['can_read']
            },
        ]

        self._create_perms()

    def set_admin_default_perms(self):
        self.perms_map = [
            {
                'model': 'user',
                'app_label': 'accounts',
                'perms': ['can_read', 'can_update', 'can_create', 'can_delete']
            },
            {
                'model': 'address',
                'app_label': 'finance',
                'perms': ['can_read', 'can_update', 'can_create', 'can_delete']
            },
            {
                'model': 'order',
                'app_label': 'finance',
                'perms': ['can_read', 'can_update', 'can_create', 'can_delete', 'can_dispatch_driver']
            },
            {
                'model': 'product',
                'app_label': 'products',
                'perms': ['can_read', 'can_update', 'can_create', 'can_delete']
            },
            {
                'model': 'productstype',
                'app_label': 'products',
                'perms': ['can_read', 'can_update', 'can_create', 'can_delete']
            },
            {
                'model': 'productscategory',
                'app_label': 'products',
                'perms': ['can_read', 'can_update', 'can_create', 'can_delete']
            },
        ]

        self._create_perms()

    def set_staff_default_perms(self):
        self.perms_map = [
            {
                'model': 'user',
                'app_label': 'accounts',
                'perms': ['can_read', 'can_update', 'can_create', 'can_delete']
            },
            {
                'model': 'address',
                'app_label': 'finance',
                'perms': ['can_read', 'can_update', 'can_delete']
            },
            {
                'model': 'order',
                'app_label': 'finance',
                'perms': ['can_read', 'can_update', 'can_dispatch_driver']
            },
            {
                'model': 'product',
                'app_label': 'products',
                'perms': ['can_read', 'can_update']
            },
            {
                'model': 'productstype',
                'app_label': 'products',
                'perms': ['can_read', 'can_update']
            },
            {
                'model': 'productscategory',
                'app_label': 'products',
                'perms': ['can_read', 'can_update']
            },
        ]

        self._create_perms()

    def _create_perms(self):
        from .models import RolePermission
        
        with transaction.atomic():
            x = 0
            for perm_map in self.perms_map:
                try:
                    content_type = ContentType.objects.get(app_label=perm_map['app_label'], model=perm_map['model'])
                except ContentType.DoesNotExist:
                    continue

                can_create = True if 'can_create' in perm_map['perms'] else False
                can_read = True if 'can_read' in perm_map['perms'] else False
                can_update = True if 'can_update' in perm_map['perms'] else False
                can_delete = True if 'can_delete' in perm_map['perms'] else False
                can_manage = True if 'can_manage' in perm_map['perms'] else False
                can_create_account = True if 'can_create_account' in perm_map['perms'] else False
                can_dispatch_driver = True if 'can_dispatch_driver' in perm_map['perms'] else False

                perm = RolePermission.objects.create(
                    role=self.role,
                    content_type=content_type,
                    can_create=can_create,
                    can_read =can_read,
                    can_update=can_update,
                    can_delete=can_delete,
                    can_manage=can_manage,
                    can_create_account=can_create_account,
                    can_dispatch_driver=can_dispatch_driver
                )
                x += 1
                # print(f'{x}/{len(self.perms_map)} Permission created for {self.role.role_name}')


