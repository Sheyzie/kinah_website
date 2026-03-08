from django.contrib import admin
from .models import User, Role, RolePermission


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['email', 'first_name', 'last_name', 'role', 'is_active']
    list_filter = ['role', 'is_active']
    search_fields = ['email', 'first_name', 'last_name']


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ['role_name', 'color', 'is_admin', 'is_editable']
    list_filter = ['is_admin', 'is_editable']


@admin.register(RolePermission)
class RolePermissionAdmin(admin.ModelAdmin):
    list_display = ['role', 'content_type', 'can_create', 'can_read', 'can_update', 'can_delete']
    list_filter = ['role']