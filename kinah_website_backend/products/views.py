from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.filters import SearchFilter, OrderingFilter
from accounts.permissions import (
    IsAdminUser, RoleBasedPermission,
    CanCreateAccount, CanDispatchDriver,
    CanManageResource
)

from .models import Product, Review, ProductsCategory, ProductsType
from .serializers import ProductSerializer, ReviewSerializer, ProductsCategorySerializer, ProductsTypeSerializer


class BaseAPIView(APIView):
    """
    Base view to wrap all responses in a consistent format.
    """

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

    def get(self, request):
        products = Product.objects.all()
        serializer = ProductSerializer(products, many=True)
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
    filter_backends = [SearchFilter, OrderingFilter]
    permission_classes = [RoleBasedPermission]

    def get(self, request, product_id=None):
        """
        If product_id is provided, show reviews by user for that product.
        Otherwise, show all reviews by the user.
        """
        reviews = Review.objects.filter(user=request.user)
        if product_id:
            reviews = reviews.filter(product_id=product_id)
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

    def get(self, request):
        products = ProductsCategory.objects.all()
        serializer = ProductsCategorySerializer(products, many=True)
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

    def get(self, request):
        products = ProductsType.objects.all()
        serializer = ProductsTypeSerializer(products, many=True)
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
   