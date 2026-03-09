from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Product, ProductImage, Review, ProductsCategory, ProductsType


User = get_user_model()


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'is_primary', 'created_at']


class ProductsCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductsCategory
        fields = '__all__'


class ProductsTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductsType
        fields = '__all__'


class ReviewSerializer(serializers.ModelSerializer):
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='user',
        write_only=True,
        required=True
    )
    user = serializers.StringRelatedField(read_only=True)  # shows username/email
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
        source='product',
        write_only=True,
        required=True
    )

    product = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Review
        fields = ['id', 'user', 'user_id', 'product', 'product_id', 'rating', 'comment', 'created_at']

    
    def get_product(self, obj):
        return {
            'id': obj.product.id,
            'name': obj.product.name,
            'image': obj.product.images.first(),
        }


class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)  # For GET
    review_score = serializers.FloatField(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=ProductsCategory.objects.all(),
        source='category',
        write_only=True,
        required=True
    )

    category = serializers.SerializerMethodField(read_only=True)
    type_id = serializers.PrimaryKeyRelatedField(
        queryset=ProductsType.objects.all(),
        source='type',
        write_only=True,
        required=True
    )

    type = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'category', 'category_id', 'type', 'type_id', 'package_type', 
            'price', 'old_price', 'discount_type', 'discount_value',
            'currency', 'description', 'quantity', 'sold', 
            'created_at', 'updated_at', 'final_price', 'review_score',
            'images'
        ]

    def get_category(self, obj):
        return {
            'id': obj.category.id,
            'name': obj.category.name,
            'color': obj.category.color
        }
    
    def get_type(self, obj):
        return {
            'id': obj.type.id,
            'name': obj.type.name,
            'color': obj.type.color
        }

    def create(self, validated_data):
        # Pop images data if sent in request
        images_data = self.context['request'].FILES.getlist('images')  # expecting multiple images

        product = Product.objects.create(**validated_data)

        # Create primary and secondary images
        for i, image in enumerate(images_data):
            ProductImage.objects.create(
                product=product,
                image=image,
                is_primary=(i == 0)  # first image is primary
            )

        return product