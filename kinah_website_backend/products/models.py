from django.db import models
from decimal import Decimal
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone
import uuid


class ProductsCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    color = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class ProductsType(models.Model):
    name = models.CharField(max_length=100, unique=True)
    color = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    DISCOUNT_TYPE_CHOICE = (
        ('percent', 'Percentage'),
        ('fixed', 'Fixed Amount'),
    )

    PACKAGE_TYPE_CHOICE = (
        ('single', 'Single'),
        ('bundle', 'Bundle'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    category = models.ForeignKey(ProductsCategory, on_delete=models.CASCADE, related_name='product_category')
    type = models.ForeignKey(ProductsType, on_delete=models.CASCADE, related_name='product_type')
    package_type = models.CharField(max_length=10, choices=PACKAGE_TYPE_CHOICE)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    old_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    discount_type = models.CharField(max_length=10, choices=DISCOUNT_TYPE_CHOICE, null=True, blank=True)
    discount_value = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    currency = models.CharField(max_length=3, default='NGN')
    description = models.TextField(null=True, blank=True)
    quantity = models.PositiveIntegerField(default=0)
    sold = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    class Meta:
        verbose_name = 'Product'
        verbose_name_plural = 'Products'
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'category', 'type'],
                name='unique_product_name_category_type'
            )
        ]
        indexes = [
            models.Index(fields=['price', 'old_price']),
            models.Index(fields=['package_type']),
            models.Index(fields=['created_at']),
        ]

    @property
    def final_price(self):
        if self.discount_type == 'percent':
            return self.price - (self.price * self.discount_value / 100)

        if self.discount_type == 'amount':
            return self.price - self.discount_value

        return self.price
    
    @property
    def review_score(self):
        avg = self.reviews.aggregate(avg_rating=models.Avg('rating'))['avg_rating']
        return round(avg, 1) if avg else 0.0
        

class ProductImage(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='images'
    )

    image = models.ImageField(upload_to='products/images/')
    is_primary = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Product Image'
        verbose_name_plural = 'Product Images'
        ordering = ['-is_primary', 'created_at']

    def save(self, *args, **kwargs):
        # Ensure only one primary image per product
        if self.is_primary:
            ProductImage.objects.filter(
                product=self.product,
                is_primary=True
            ).update(is_primary=False)

        # Limit secondary images to 4
        if not self.is_primary:
            secondary_count = ProductImage.objects.filter(
                product=self.product,
                is_primary=False
            ).count()

            if secondary_count >= 4:
                raise ValueError("A product can only have 4 secondary images.")

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product.name} Image"


class Review(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='reviews'
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reviews'
    )

    rating = models.PositiveSmallIntegerField()
    comment = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Review'
        verbose_name_plural = 'Reviews'
        ordering = ['-created_at']
        unique_together = ['product', 'user']

    def __str__(self):
        return f"{self.user} - {self.product} ({self.rating})"
    
