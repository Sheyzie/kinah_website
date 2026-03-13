from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import (
    VehicleViewSet, DispatchViewSet
)

router = DefaultRouter()

router.register(r'vehicles', VehicleViewSet, basename='vehicle')
router.register(r'dispatches', DispatchViewSet, basename='dispatch')

urlpatterns = router.urls