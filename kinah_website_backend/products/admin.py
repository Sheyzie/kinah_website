from django.contrib import admin
from .models import Product, ProductImage, ProductsCategory, ProductsType, Review


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'package_type', 'price', 'quantity']
    list_filter = ['category', 'type']
    search_fields = ['name', 'category', 'type']


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ['product__name', 'is_primary']
    list_filter = ['product__name', 'is_primary']
    search_fields = ['product__name']


@admin.register(ProductsCategory)
class ProductsCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'color']
    list_filter = ['name', 'color']
    search_fields = ['name']


@admin.register(ProductsType)
class ProductsTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'color']
    list_filter = ['name', 'color']
    search_fields = ['name']


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['product__name', 'user__first_name', 'user__last_name']
    list_filter = ['product__name', 'rating']
    search_fields = ['product__name']
