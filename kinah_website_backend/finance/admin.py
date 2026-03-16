from django.contrib import admin
from .models import (
    Address, Order, OrderItem,
    OrderStatusHistory,
    Coupon, Payment
)


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ['user__email', 'full_name', 'state', 'country']
    list_filter = ['state', 'country']
    search_fields = ['postal_code', 'state', 'country']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'payment_status', 'customer_email', 'status']
    list_filter = ['payment_status', 'status', 'payment_method']
    search_fields = ['-created_at', 'order_number', 'tracking_number']


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['product_name', 'product_category', 'quantity', 'unit_price']
    list_filter = ['product_category', 'product_type', 'package_type']
    search_fields = ['-created_at', 'product_name', 'product_type', 'product_category']


@admin.register(OrderStatusHistory)
class OrderStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ['order__id', 'status', 'created_by__email']
    list_filter = ['status']
    search_fields = ['-created_at']


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ['code', 'discount_value', 'discount_type', 'valid_to', 'is_active']
    list_filter = ['discount_type', 'valid_from', 'valid_to']
    search_fields = ['-created_at', 'valid_from', 'valid_to']


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['transaction_id', 'amount', 'payment_method', 'status']
    list_filter = ['payment_method', 'status']
    search_fields = ['-created_at', 'transaction_id', 'payment_method']