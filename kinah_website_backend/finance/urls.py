from rest_framework.routers import DefaultRouter
from .views import AddressViewSet, OrderViewSet, CouponViewSet, PaymentViewSet

router = DefaultRouter()

router.register(r'addresses', AddressViewSet, basename='address')
router.register(r'orders', OrderViewSet, basename='order')
router.register(r'coupons', CouponViewSet, basename='coupon')
router.register(r'payments', PaymentViewSet, basename='payment')

urlpatterns = router.urls