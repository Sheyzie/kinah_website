from rest_framework import routers
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    UserViewSet,
    SetPasswordView,
    RoleViewSet,
    RolePermissionViewSet,
    password_reset_request,
    LogoutView,
    LogoutAllView
)

from .custom_token_view import CustomTokenObtainPairView
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

router = routers.DefaultRouter()
router.register(r'users', UserViewSet, basename='users')
router.register(r'roles', RoleViewSet, basename='roles')
router.register(r'permissions', RolePermissionViewSet, basename='roleperms')

urlpatterns = [
    # JWT Token endpoints
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Account management endpoints
    path('accounts/set-password/', SetPasswordView.as_view()),
    path('accounts/password-reset/', password_reset_request, name='password_reset'),
    path('accounts/logout/', LogoutView.as_view(), name='logout'),
    path('accounts/logout-all/', LogoutAllView.as_view(), name='logout_users'),
    path('roles/user-counts/', views.role_user_counts, name='role-user-counts'),
    path('roles/specific-user-counts/', views.specific_role_user_counts, name='specific-role-user-counts'),
    path('content-types/', views.get_content_types, name='content_types'),
    path('permission-options/', views.get_permission_options, name='permission_options'),
    path('dashboard/', views.dashboard, name='dashboard')
]

# Add router URLs
urlpatterns += router.urls
