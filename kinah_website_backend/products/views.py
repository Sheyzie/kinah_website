from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle
from rest_framework.permissions import AllowAny, IsAuthenticated
from accounts.permissions import (
    IsAdminUser, RoleBasedPermission,
    CanManageResource
)

from .models import Product, Review, ProductsCategory, ProductsType
from .serializers import ProductSerializer, ReviewSerializer, ProductsCategorySerializer, ProductsTypeSerializer


class BaseAPIView(APIView):
    """
    Base view to wrap all responses in a consistent format.
    """
    filter_backends = [SearchFilter, OrderingFilter]
    throttle_classes = [UserRateThrottle]

    def success(self, data=None, message="Success", code=status.HTTP_200_OK):
        return Response({
            "status": "success",
            "message": message,
            "data": data
        }, status=code)

    def failure(self, errors=None, message="Failed", code=status.HTTP_400_BAD_REQUEST):
        return Response({
            "status": "failure",
            "message": message,
            "errors": errors
        }, status=code)


class ProductListCreateView(BaseAPIView):
    """
    GET: List all products
    POST: Create a product with images
    """
    permission_classes = [RoleBasedPermission]
    search_fields = ['name', 'type__name', 'category__name']
    ordering_fields = ['name', 'type__name', 'category__name', 'created_at', 'updated_at']
    ordering = ['-created_at']

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return super().get_permissions()

    def get(self, request):
        search_filter = SearchFilter()
        ordering_filter = OrderingFilter()

        queryset = Product.objects.all()

        queryset = search_filter.filter_queryset(request, queryset, self)
        queryset = ordering_filter.filter_queryset(request, queryset, self)

        serializer = ProductSerializer(queryset, many=True)
        return self.success(data=serializer.data)

    def post(self, request):
        serializer = ProductSerializer(data=request.data, context={"request": request})
        if serializer.is_valid(raise_exception=True):
            product = serializer.save()
            return self.success(data=ProductSerializer(product).data, message="Product created", code=201)
        return self.failure(errors=serializer.errors, message="Product creation failed")
    

class ProductDetailView(BaseAPIView):
    """
    GET: Retrieve a single product
    PUT: Update product
    DELETE: Delete product
    """
    permission_classes = [RoleBasedPermission]

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return super().get_permissions()

    def get_object(self, pk):
        try:
            return Product.objects.get(pk=pk)
        except Product.DoesNotExist:
            return None

    def get(self, request, pk):
        product = self.get_object(pk)
        if not product:
            return self.failure(message="Product not found", code=404)
        serializer = ProductSerializer(product)
        return self.success(data=serializer.data)

    def put(self, request, pk):
        if not pk:
            return self.failure(message="Product ID is required", code=400)
        
        product = self.get_object(pk)
        if not product:
            return self.failure(message="Product not found", code=404)

        serializer = ProductSerializer(product, data=request.data, context={"request": request}, partial=True)
        if serializer.is_valid(raise_exception=True):
            product = serializer.save()
            return self.success(data=ProductSerializer(product).data, message="Product updated")
        return self.failure(errors=serializer.errors, message="Update failed")

    def delete(self, request, pk):
        if not pk:
            return self.failure(message="Product ID is required", code=400)
        
        product = self.get_object(pk)
        if not product:
            return self.failure(message="Product not found", code=404)
        product.delete()
        return self.success(message="Product deleted", data=None)
    

class ReviewListCreateView(BaseAPIView):
    """
    GET: List reviews for a product
    POST: Create a review for a product
    """
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [RoleBasedPermission]
    search_fields = ['product__name', 'product__type__name', 'product__category__name']
    ordering_fields = ['product__name', 'product__type__name', 'product__category__name', 'created_at', 'updated_at']
    ordering = ['-created_at']


    def get_permissions(self):
        if self.request.method in ['GET', 'POST']:
            return [IsAuthenticated()]
        return super().get_permissions()

    def get(self, request, product_id=None):
        """
        If product_id is provided, show reviews by user for that product.
        Otherwise, show all reviews by the user.
        """
        search_filter = SearchFilter()
        ordering_filter = OrderingFilter()

        user = self.request.user
        has_access = user.is_authenticated and (user.is_superuser or (hasattr(user, 'role') and user.role.is_admin))
        
        queryset = Review.objects.all()
        if not has_access:
            queryset = queryset.filter(user=user)

        queryset = search_filter.filter_queryset(request, queryset, self)
        queryset = ordering_filter.filter_queryset(request, queryset, self)

        if product_id:
            reviews = queryset.filter(product_id=product_id)
        serializer = ReviewSerializer(reviews, many=True)
        return self.success(data=serializer.data)

    def post(self, request, product_id):
        if not product_id:
            return self.failure(message="Product ID is required", code=400)
        
        data = request.data.copy()
        data['product_id'] = product_id
        data['user_id'] = request.user.id 
        serializer = ReviewSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            review = serializer.save()
            return self.success(data=ReviewSerializer(review).data, message="Review created", code=201)
        return self.failure(errors=serializer.errors, message="Review creation failed")

 
class ProductCategoryListCreateView(BaseAPIView):
    """
    GET: List all products categories
    POST: Create a product categories
    """
    permission_classes = [RoleBasedPermission]
    search_fields = ['name']
    ordering_fields = ['name', 'created_at', 'updated_at']
    ordering = ['-created_at']


    def get(self, request):
        search_filter = SearchFilter()
        ordering_filter = OrderingFilter()

        queryset = ProductsCategory.objects.all()

        queryset = search_filter.filter_queryset(request, queryset, self)
        queryset = ordering_filter.filter_queryset(request, queryset, self)

        serializer = ProductsCategorySerializer(queryset, many=True)
        return self.success(data=serializer.data)

    def post(self, request):
        serializer = ProductsCategorySerializer(data=request.data, context={"request": request})
        if serializer.is_valid(raise_exception=True):
            product = serializer.save()
            return self.success(data=ProductsCategorySerializer(product).data, message="Product category created successfully", code=201)
        return self.failure(errors=serializer.errors, message="Product category creation failed")
    

class ProductCategoryDetailView(BaseAPIView):
    """
    PUT: Update product category
    DELETE: Delete product category
    """
    permission_classes = [RoleBasedPermission]

    def get_object(self, pk):
        try:
            return ProductsCategory.objects.get(pk=pk)
        except ProductsCategory.DoesNotExist:
            return None

    def put(self, request, pk):
        if not pk:
            return self.failure(message="Product ID is required", code=400)
        
        category = self.get_object(pk)
        if not category:
            return self.failure(message="Product category not found", code=404)

        serializer = ProductsCategorySerializer(category, data=request.data, context={"request": request}, partial=True)
        if serializer.is_valid(raise_exception=True):
            category = serializer.save()
            return self.success(data=ProductsCategorySerializer(category).data, message="Product category updated")
        return self.failure(errors=serializer.errors, message="Update failed for product category")

    def delete(self, request, pk):
        if not pk:
            return self.failure(message="Product ID is required", code=400)
        
        category = self.get_object(pk)
        if not category:
            return self.failure(message="Product category not found", code=404)
        category.delete()
        return self.success(message="Product category deleted", data=None)
   
 
class ProductTypeListCreateView(BaseAPIView):
    """
    GET: List all products categories
    POST: Create a product categories
    """
    permission_classes = [RoleBasedPermission]
    search_fields = ['name']
    ordering_fields = ['name', 'created_at', 'updated_at']
    ordering = ['-created_at']

    def get(self, request):
        search_filter = SearchFilter()
        ordering_filter = OrderingFilter()

        queryset = ProductsType.objects.all()

        queryset = search_filter.filter_queryset(request, queryset, self)
        queryset = ordering_filter.filter_queryset(request, queryset, self)

        serializer = ProductsTypeSerializer(queryset, many=True)
        return self.success(data=serializer.data)

    def post(self, request):
        serializer = ProductsTypeSerializer(data=request.data, context={"request": request})
        if serializer.is_valid(raise_exception=True):
            product = serializer.save()
            return self.success(data=ProductsTypeSerializer(product).data, message="Product type created successfully", code=201)
        return self.failure(errors=serializer.errors, message="Product type creation failed")
    

class ProductTypeDetailView(BaseAPIView):
    """
    PUT: Update product type
    DELETE: Delete product type
    """
    permission_classes = [RoleBasedPermission]

    def get_object(self, pk):
        try:
            return ProductsType.objects.get(pk=pk)
        except ProductsType.DoesNotExist:
            return None

    def put(self, request, pk):
        if not pk:
            return self.failure(message="Product ID is required", code=400)
        
        product_type = self.get_object(pk)
        if not product_type:
            return self.failure(message="Product type not found", code=404)

        serializer = ProductsTypeSerializer(product_type, data=request.data, context={"request": request}, partial=True)
        if serializer.is_valid(raise_exception=True):
            type = serializer.save()
            return self.success(data=ProductsTypeSerializer(product_type).data, message="Product type updated")
        return self.failure(errors=serializer.errors, message="Update failed for product type")

    def delete(self, request, pk):
        if not pk:
            return self.failure(message="Product ID is required", code=400)
        
        product_type = self.get_object(pk)
        if not product_type:
            return self.failure(message="Product type not found", code=404)
        product_type.delete()
        return self.success(message="Product type deleted", data=None)
   