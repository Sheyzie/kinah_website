from django.urls import path
from .views import (
    ProductListCreateView, 
    ProductDetailView, 
    ReviewListCreateView,
    ProductCategoryListCreateView,
    ProductCategoryDetailView,
    ProductTypeListCreateView,
    ProductTypeDetailView
)

urlpatterns = [
    path('', ProductListCreateView.as_view(), name='product-list-create'),
    path('<uuid:pk>/', ProductDetailView.as_view(), name='product-detail'),
    path('categories', ProductCategoryListCreateView.as_view(), name='category-list-create'),
    path('categories/<uuid:pk>/', ProductCategoryDetailView.as_view(), name='category-detail'),
    path('types', ProductTypeListCreateView.as_view(), name='types-list-create'),
    path('types/<uuid:pk>/', ProductTypeDetailView.as_view(), name='type-detail'),
    path('reviews/', ReviewListCreateView.as_view(), name='review-list-create'),  # all user reviews
    path('reviews/<uuid:product_id>/', ReviewListCreateView.as_view(), name='review-detail'),  # for a specific product
]