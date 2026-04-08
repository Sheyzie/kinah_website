from django.db import models
from django.conf import settings
import uuid


class Vehicle(models.Model):
    vehicle_type = models.CharField(max_length=50)
    vehicle_brand = models.CharField(max_length=50)
    plate_number = models.CharField(max_length=50, unique=True)
    plate_state = models.CharField(max_length=50)
    plate_country = models.CharField(max_length=50)
    color = models.CharField(max_length=20)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Vehicle'
        ordering = ['vehicle_brand']

    def __str__(self):
        return f'{self.vehicle_brand} - {self.plate_number}'


class Dispatch(models.Model):
    STATUS_CHOICE = (
        ('available', 'Available'),
        ('dispatched', 'Dispatched'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    driver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='dispatch',
        null=True,
        blank=True
    )

    company_name = models.CharField(max_length=50)
    company_address = models.ForeignKey(
        'finance.Address', 
        on_delete=models.SET_NULL, 
        null=True, blank=True,
        related_name='dispatches'
    )

    vehicle = models.OneToOneField(
        Vehicle,
        on_delete=models.CASCADE,
        related_name='dispatch'
    )

    cost_per_km = models.DecimalField(max_digits=8, decimal_places=2, default=0)

    is_active = models.BooleanField(default=False, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICE, default='available')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Dispatch'
        ordering = ['-created_at']

    def __str__(self):
        if self.driver:
            return f'{self.driver.full_name} (Dispatcher)'
        return f'Dispatch {self.id}'

    @property
    def total_order(self):
        return self.dispatched_orders.all().count()

    @property
    def last_order(self):
        return self.dispatched_orders.order_by('-created_at').first()
