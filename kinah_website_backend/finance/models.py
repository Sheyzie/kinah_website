from django.db import models, transaction
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.db.models import Sum
from django.conf import settings
import uuid


DISCOUNT_TYPE_CHOICE = (
    ('percent', 'Percentage'),
    ('fixed', 'Fixed Amount'),
)

PAYMENT_METHOD = (
    ('credit_card', 'Credit Card'),
    ('debit_card', 'Debit Card'),
    ('paystack', 'Paystack'),
    ('bank_tranfer', 'Bank Transfer'),
)

class Address(models.Model):
    '''
    Shipping and billing address model
    '''
    ADDRESS_TYPE = (
        ('shipping', 'Shipping'),
        ('billing', 'Billing'),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='address',
        null=True,
        blank=True
    )
    address_type = models.CharField(max_length=10, choices=ADDRESS_TYPE)
    full_name = models.CharField(max_length=100)
    street_address = models.CharField(max_length=255)
    apartment_address = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20, null=True, blank=True)
    country = models.CharField(max_length=100)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Addresses'

    def __str__(self):
        return f'{self.full_name} - {self.street_address}'


class Order(models.Model):
    '''
    Main Order model
    '''
    ORDER_STATUS = (
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('confirmed', 'Confirmed'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    )

    PAYMENT_STATUS = (
        ('pending', 'Pending'),
        ('partial', 'Partial'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='orders',
        null=True,
        blank=True
    )

    # address
    shipping_address = models.ForeignKey(
        Address, 
        on_delete=models.SET_NULL, 
        null=True, blank=True,
        related_name='shipping_orders'
    )
    billing_address = models.ForeignKey(
        Address,
        on_delete=models.SET_NULL, 
        null=True, blank=True,
        related_name='billing_orders'
    )

    # order details
    order_number = models.CharField(max_length=50, unique=True)
    status = models.CharField(max_length=20, choices=ORDER_STATUS, default='pending')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='pending')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD)

    # financial fields
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    tax_name = models.CharField(max_length=20, null=True, blank=True)
    tax_type = models.CharField(max_length=20, choices=DISCOUNT_TYPE_CHOICE, null=True, blank=True)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    discount_type = models.CharField(max_length=10, choices=DISCOUNT_TYPE_CHOICE, null=True, blank=True)
    discount_value = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # shipping tracking
    tracking_number = models.CharField(max_length=100, unique=True)
    shipping_carrier = models.CharField(max_length=50, null=True, blank=True)
    estimated_delivery = models.DateField(null=True, blank=True)

    # additional information
    customer_note = models.TextField(null=True, blank=True)
    admin_note = models.TextField(null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True,blank=True)

    # discount coupon
    coupon_code = models.CharField(max_length=50, null=True, blank=True)

    # timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    shipped_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Order #{self.order_number}'
    
    def save(self, *args, **kwargs):
        if not self.order_number:
            # generate unique order number
            last_order = Order.objects.order_by('-id').first()
            if last_order:
                last_id = last_order.id
                new_id = last_id + 1
            else:
                new_id = 1
            self.order_number = f'ORD-{new_id:06d}'
        return super().save(*args, **kwargs)
    
    @property
    def subtotal(self):
        return sum(item.total_price for item in self.items.all())
    
    @property
    def discount(self):
        if self.discount_type == 'percent':
            return self.subtotal - (self.subtotal * self.discount_value / 100)

        if self.discount_type == 'amount':
            return self.subtotal - self.discount_value
        
        return 0

    @property
    def total_amount(self):
        total_amount = self.subtotal + self.shipping_cost + self.tax_amount - self.discount
        return total_amount
    
    @property
    def item_count(self):
        return self.items.count()


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(
        'products.Product', 
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    # snapshot of the product at a time of purchase
    product_name = models.CharField(max_length=100)
    product_category = models.CharField(max_length=100)
    product_type = models.CharField(max_length=100)
    package_type = models.CharField(max_length=100)

    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    unit_price = models.DecimalField(max_digits=8, decimal_places=2)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.quantity}x {self.product.name} in Order #{self.order.order_number}'
    
    @property
    def total_price(self):
        return self.unit_price * self.quantity


class OrderStatusHistory(models.Model):
    '''
    Track oreder status change
    '''
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='status_history')
    status = models.CharField(max_length=20)
    notes = models.TextField(null=True, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Order status histories'

    def __str__(self):
        return f'{self.order.order_number} - {self.get_status_display()}'
    

class Coupon(models.Model):
    '''
    Discount coupon
    '''
    code = models.CharField(max_length=50, unique=True)
    discount_type = models.CharField(max_length=10, choices=DISCOUNT_TYPE_CHOICE, null=True, blank=True)
    discount_value = models.DecimalField(max_digits=6, decimal_places=2, default=0)

    # usage limits
    max_uses = models.PositiveIntegerField(null=True, blank=True)
    used_count = models.PositiveIntegerField(default=0)
    per_user_limit = models.PositiveIntegerField(default=1)

    # validity period
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()

    # minimum order amount
    min_order_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    # applicable products/category
    products = models.ManyToManyField(
        'products.Product',
        blank=True
    )
    category = models.ManyToManyField(
        'products.ProductsCategory',
        blank=True
    )

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.code
    
    @property
    def is_valid(self):
        from django.utils import timezone
        now = timezone.now()
        return (
            self.is_active and 
            self.valid_from <= now <= self.valid_to and
            (self.max_uses is None or self.used_count < self.max_uses)
        )
    

class Payment(models.Model):
    '''
    Payment transactions
    '''
    PAYMENT_STATUS = (
        ('initiated', 'Initiated'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    )

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='payments')
    transaction_id = models.CharField(max_length=100, unique=True)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS)

    # gateway response
    gateway_response = models.JSONField(default=dict)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Payment {self.transaction_id} for Order #{self.order.order_number}'
    
    @transaction.atomic
    def save(self, *args, **kwargs):

        # default status for new payment
        if not self.pk and not self.status:
            self.status = "initiated"

        super().save(*args, **kwargs)

        # only process completed payments
        if self.status == "completed":

            total_paid = self.order.payments.filter(
                status="completed"
            ).aggregate(
                total=Sum("amount")
            )["total"] or 0

            order_total = self.order.total_amount

            # prevent overpayment
            if total_paid > order_total:
                raise ValidationError("Payment exceeds order total.")

            # update order payment status
            if total_paid < order_total:
                self.order.payment_status = "partial"

            elif total_paid == order_total:
                self.order.payment_status = "paid"

            self.order.save(update_fields=["payment_status"])



