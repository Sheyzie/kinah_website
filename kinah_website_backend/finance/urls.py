from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import (
    AddressViewSet, OrderViewSet, 
    CouponViewSet, PaymentViewSet, PaystackWebhook
)

router = DefaultRouter()

router.register(r'addresses', AddressViewSet, basename='address')
router.register(r'orders', OrderViewSet, basename='order')
router.register(r'coupons', CouponViewSet, basename='coupon')
router.register(r'payments', PaymentViewSet, basename='payment')

urlpatterns = [
    path('payment/webhook/', PaystackWebhook.as_view(), name='paystack-webhook'),
]

urlpatterns += router.urls