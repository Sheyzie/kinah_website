"""
URL configuration for kinah_website project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from rest_framework.permissions import AllowAny
from django.conf.urls.static import static
from drf_spectacular.views import (
    SpectacularAPIView, 
    SpectacularSwaggerView, 
    SpectacularRedocView
)
from django.views.generic import RedirectView

# Base URL for the API
base_url = 'api/v1'

urlpatterns = [
    # base API
    path("", RedirectView.as_view(url=f"/{base_url}/docs/", permanent=False)),

    # Admin route
    path(f'{base_url}/admin/', admin.site.urls),

    # Include app-specific routes
    path(f'{base_url}/', include('accounts.urls')),

    # Schema and API Documentation
    path(f'{base_url}/schema/', SpectacularAPIView.as_view(), name='schema'),
    path(f'{base_url}/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path(f'{base_url}/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
