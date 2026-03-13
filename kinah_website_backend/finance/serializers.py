from rest_framework import serializers
from django.utils import timezone
from django.db import transaction
from .models import (
    Address, Order, OrderItem, OrderStatusHistory, 
    Coupon, Payment, DISCOUNT_TYPE_CHOICE
)
from products.models import Product, ProductsCategory
import uuid


class AddressSerializer(serializers.ModelSerializer):
    """
    Serializer for Address model with user assignment
    """
    user = serializers.PrimaryKeyRelatedField(
        read_only=True,
        default=serializers.CurrentUserDefault()
    )
    
    class Meta:
        model = Address
        fields = [
            'id', 'user', 'address_type', 'full_name', 'street_address',
            'apartment_address', 'city', 'state', 'postal_code', 'country',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'user']
    
    def validate(self, data):
        """
        Validate address data
        """
        if not data.get('full_name'):
            raise serializers.ValidationError(
                {"full_name": "Full name is required."}
            )
        
        if not data.get('street_address'):
            raise serializers.ValidationError(
                {"street_address": "Street address is required."}
            )
        
        return data


class OrderItemSerializer(serializers.ModelSerializer):
    """
    Serializer for OrderItem with product validation
    """
    product_name = serializers.CharField(read_only=True)
    product_category = serializers.CharField(read_only=True)
    product_type = serializers.CharField(read_only=True)
    package_type = serializers.CharField(read_only=True)
    total_price = serializers.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        read_only=True
    )
    
    class Meta:
        model = OrderItem
        fields = [
            'id', 'product', 'product_name', 'product_category',
            'product_type', 'package_type', 'quantity', 'unit_price',
            'total_price', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate(self, data):
        """
        Validate order item data
        """
        if data.get('quantity', 0) <= 0:
            raise serializers.ValidationError(
                {"quantity": "Quantity must be greater than 0."}
            )
        
        if data.get('unit_price', 0) <= 0:
            raise serializers.ValidationError(
                {"unit_price": "Unit price must be greater than 0."}
            )
        
        # Validate product exists and has sufficient stock
        product = data.get('product')
        if product and product.quantity < data.get('quantity', 0):
            raise serializers.ValidationError(
                {"quantity": f"Insufficient stock. Available: {product.quantity}"}
            )
        
        return data


class OrderStatusHistorySerializer(serializers.ModelSerializer):
    """
    Serializer for OrderStatusHistory
    """
    created_by = serializers.PrimaryKeyRelatedField(
        read_only=True,
        default=serializers.CurrentUserDefault()
    )
    created_by_name = serializers.CharField(
        source='created_by.get_full_name',
        read_only=True
    )
    
    class Meta:
        model = OrderStatusHistory
        fields = [
            'id', 'order', 'status', 'notes', 
            'created_by', 'created_by_name', 'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'created_by']


class OrderListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for list views
    """
    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_full_name = serializers.SerializerMethodField()
    item_count = serializers.IntegerField(read_only=True)
    total_amount = serializers.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        read_only=True
    )
    
    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'user', 'user_email', 'user_full_name',
            'status', 'payment_status', 'payment_method', 'total_amount',
            'item_count', 'created_at'
        ]
        read_only_fields = ['id', 'order_number', 'created_at']
    
    def get_user_full_name(self, obj):
        if obj.user:
            return obj.user.get_full_name()
        return None


class OrderDetailSerializer(serializers.ModelSerializer):
    """
    Detailed serializer for single order view
    """
    shipping_address = AddressSerializer(read_only=True)
    billing_address = AddressSerializer(read_only=True)
    items = OrderItemSerializer(many=True, read_only=True)
    dispatch = serializers.SerializerMethodField(read_only=True)
    status_history = OrderStatusHistorySerializer(
        many=True, 
        read_only=True,
        source='status_history.all'
    )
    payments = serializers.PrimaryKeyRelatedField(
        many=True, 
        read_only=True,
        source='payments.all'
    )
    
    # Computed fields
    subtotal = serializers.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        read_only=True
    )
    discount = serializers.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        read_only=True
    )
    total_amount = serializers.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        read_only=True
    )
    
    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'user', 'shipping_address', 'billing_address',
            'status', 'payment_status', 'payment_method', 'shipping_cost',
            'tax_name', 'tax_type', 'tax_amount', 'discount_type', 'discount_value',
            'subtotal', 'discount', 'total_amount', 'tracking_number',
            'shipping_carrier', 'estimated_delivery', 'customer_note', 'admin_note',
            'ip_address', 'coupon_code', 'items', 'status_history', 'payments', 'dispatch'
            'created_at', 'updated_at', 'paid_at', 'shipped_at', 'delivered_at'
        ]
        read_only_fields = [
            'id', 'order_number', 'user', 'created_at', 'updated_at',
            'paid_at', 'shipped_at', 'delivered_at'
        ]

    def get_dispatch(self, obj):
        if not obj.dispatch:
            return None
        return {
            'id': obj.dispatch.id,
            'driver': obj.dispatch.driver.full_name if obj.dispatch.driver else None,
            'vehicle': {
                    'id': obj.dispatch.vehicle.id,
                    'vehicle_type': obj.dispatch.vehicle.vehicle_type,
                    'plate_number': obj.dispatch.vehicle.plate_number
                },
        }

class OrderCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating and updating orders
    """
    items = OrderItemSerializer(many=True)
    shipping_address_id = serializers.PrimaryKeyRelatedField(
        queryset=Address.objects.all(),
        source='shipping_address',
        required=False,
        allow_null=True
    )
    billing_address_id = serializers.PrimaryKeyRelatedField(
        queryset=Address.objects.all(),
        source='billing_address',
        required=False,
        allow_null=True
    )
    
    class Meta:
        model = Order
        fields = [
            'shipping_address_id', 'billing_address_id', 'payment_method',
            'shipping_cost', 'tax_name', 'tax_type', 'tax_amount',
            'discount_type', 'discount_value', 'customer_note',
            'coupon_code', 'items'
        ]
    
    def validate_items(self, value):
        """
        Validate that items list is not empty
        """
        if not value:
            raise serializers.ValidationError(
                "Order must contain at least one item."
            )
        return value
    
    def validate_coupon_code(self, value):
        """
        Validate coupon code if provided
        """
        if value:
            try:
                coupon = Coupon.objects.get(
                    code=value,
                    is_active=True,
                    valid_from__lte=timezone.now(),
                    valid_to__gte=timezone.now()
                )
                
                # Check max uses
                if coupon.max_uses and coupon.used_count >= coupon.max_uses:
                    raise serializers.ValidationError(
                        "This coupon has reached its maximum usage limit."
                    )
                
                # Check if user has already used this coupon
                user = self.context['request'].user
                if user.is_authenticated and coupon.per_user_limit:
                    user_usage = Order.objects.filter(
                        user=user,
                        coupon_code=value,
                        payment_status='paid'
                    ).count()
                    if user_usage >= coupon.per_user_limit:
                        raise serializers.ValidationError(
                            "You have already used this coupon."
                        )
                
            except Coupon.DoesNotExist:
                raise serializers.ValidationError("Invalid or expired coupon code.")
        
        return value
    
    @transaction.atomic
    def create(self, validated_data):
        """
        Create order with items
        """
        items_data = validated_data.pop('items')
        user = self.context['request'].user
        validated_data['payment_status'] = 'pending'
        validated_data['status'] = 'pending'
        validated_data.pop('dispatch', None)
        
        # Create order
        order = Order.objects.create(
            user=user if user.is_authenticated else None,
            **validated_data
        )
        
        # Create order items and update stock
        for item_data in items_data:
            product = item_data.get('product')
            
            # Snapshot product details
            if product:
                item_data['product_name'] = product.name
                item_data['product_category'] = product.category.name
                item_data['product_type'] = product.type.name
                item_data['package_type'] = product.package_type

            
            # Create order item
            OrderItem.objects.create(order=order, **item_data)
            
            # Update stock
            if product:
                product.quantity -= item_data['quantity']
                product.save()
        
        # Create initial status history
        OrderStatusHistory.objects.create(
            order=order,
            status=order.status,
            notes="Order created",
            created_by=user if user.is_authenticated else None
        )
        
        return order
    
    @transaction.atomic
    def update(self, instance, validated_data):
        """
        Update order and handle items if provided
        """
        old_status = instance.status
        items_data = validated_data.pop('items', None)
        new_status = validated_data.get('status', old_status)
        validated_data.pop("status", None)
        validated_data.pop("payment_status", None)
        validated_data.pop('dispatch', None)
        
        # Update order fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        # Handle status change
        instance.save()
        
        # Create status history if status changed
        if old_status != new_status:
            OrderStatusHistory.objects.create(
                order=instance,
                status=new_status,
                notes=f"Status changed from {old_status} to {new_status}",
                created_by=self.context.get("request").user
            )
        
        # Update items if provided
        if items_data is not None:
            # Remove existing items
            instance.items.all().delete()
            
            # Create new items
            for item_data in items_data:
                OrderItem.objects.create(order=instance, **item_data)
        
        return instance


class CouponSerializer(serializers.ModelSerializer):
    """
    Serializer for Coupon model
    """
    is_valid = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Coupon
        fields = [
            'id', 'code', 'discount_type', 'discount_value', 'max_uses',
            'used_count', 'per_user_limit', 'valid_from', 'valid_to',
            'min_order_amount', 'products', 'category', 'is_active',
            'is_valid', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'used_count', 'created_at', 'updated_at']
    
    def validate(self, data):
        """
        Validate coupon data
        """
        if data.get('valid_from') and data.get('valid_to'):
            if data['valid_from'] >= data['valid_to']:
                raise serializers.ValidationError(
                    "Valid to date must be after valid from date."
                )
        
        if data.get('max_uses') and data.get('max_uses') < 0:
            raise serializers.ValidationError(
                {"max_uses": "Max uses must be positive or null."}
            )
        
        return data


class CouponValidateSerializer(serializers.Serializer):
    """
    Serializer for validating coupons
    """
    code = serializers.CharField(max_length=50)
    subtotal = serializers.DecimalField(
        max_digits=10, 
        decimal_places=2,
        required=False,
        default=0
    )
    
    def validate(self, data):
        """
        Validate and return coupon details
        """
        try:
            coupon = Coupon.objects.get(
                code=data['code'],
                is_active=True,
                valid_from__lte=timezone.now(),
                valid_to__gte=timezone.now()
            )
            
            # Check max uses
            if coupon.max_uses and coupon.used_count >= coupon.max_uses:
                raise serializers.ValidationError(
                    "This coupon has reached its maximum usage limit."
                )
            
            # Check minimum order amount
            if (coupon.min_order_amount and 
                data.get('subtotal', 0) < coupon.min_order_amount):
                raise serializers.ValidationError(
                    f"Minimum order amount of {coupon.min_order_amount} required."
                )
            
            data['coupon'] = coupon
            
        except Coupon.DoesNotExist:
            raise serializers.ValidationError("Invalid or expired coupon code.")
        
        return data
    
    def to_representation(self, instance):
        """
        Return coupon details with calculated discount
        """
        coupon = instance['coupon']
        subtotal = instance.get('subtotal', 0)
        
        # Calculate discount
        if coupon.discount_type == 'percent':
            discount_amount = (subtotal * coupon.discount_value / 100)
        else:
            discount_amount = coupon.discount_value
        
        return {
            'code': coupon.code,
            'discount_type': coupon.discount_type,
            'discount_value': coupon.discount_value,
            'discount_amount': discount_amount,
            'valid_from': coupon.valid_from,
            'valid_to': coupon.valid_to
        }


class PaymentSerializer(serializers.ModelSerializer):
    """
    Serializer for Payment model
    """
    class Meta:
        model = Payment
        fields = [
            'id', 'order', 'transaction_id', 'payment_method', 'amount',
            'status', 'gateway_response', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'status', 'created_at', 'updated_at', 'transaction_id']
    
    def validate(self, data):
        """
        Validate payment data
        """
        if data.get('amount', 0) <= 0:
            raise serializers.ValidationError(
                {"amount": "Amount must be greater than 0."}
            )
        
        # Check if payment amount doesn't exceed order total
        order = data.get('order')
        if order:
            total_paid = sum(p.amount for p in order.payments.filter(status='completed'))
            if total_paid + data['amount'] > order.total_amount:
                raise serializers.ValidationError(
                    {"amount": "Payment amount exceeds order total."}
                )
            
        data.pop('status', None)
        
        return data
    
    def create(self, validated_data):
        """
        Create payment with transaction ID
        """
        validated_data['transaction_id'] = str(uuid.uuid4()).replace('-', '')[:20]
        validated_data['status'] = 'initiated'
        return super().create(validated_data)
        

class OrderStatusUpdateSerializer(serializers.Serializer):
    """
    Serializer for updating order status
    """
    status = serializers.ChoiceField(choices=Order.ORDER_STATUS)
    notes = serializers.CharField(required=False, allow_blank=True)
    
    def update_status(self, instance):
        """
        Update order status and create history
        """
        old_status = instance.status
        new_status = self.validated_data['status']

        if old_status != new_status and new_status in {"cancelled", "refunded"}:
            for item in instance.items.select_related("product"):
                product = item.product
                product.quantity += item.quantity
                product.save(update_fields=["quantity"])
        
        if old_status != new_status:
            instance.status = new_status
            instance.save()
            
            # Create status history
            OrderStatusHistory.objects.create(
                order=instance,
                status=new_status,
                notes=self.validated_data.get('notes', ''),
                created_by=self.context['request'].user
            )
            
            # Update timestamps based on status
            if new_status == 'shipped':
                instance.shipped_at = timezone.now()
                instance.save()
            elif new_status == 'delivered':
                instance.delivered_at = timezone.now()
                instance.save()
            # elif new_status == 'paid':
            #     instance.paid_at = timezone.now()
            #     instance.payment_status = 'paid'
            #     instance.save()
        
        return instance