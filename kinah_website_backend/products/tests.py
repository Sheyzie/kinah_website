from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model
from accounts.utils import printInJSON
from .models import Product, ProductsCategory, ProductsType, Review, ProductImage
from io import BytesIO
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image


User = get_user_model()


def get_test_image(name='test.jpg'):
    """Generate a simple image for testing"""
    file = BytesIO()
    image = Image.new('RGB', (100, 100), color='red')
    image.save(file, 'jpeg')
    file.seek(0)
    return SimpleUploadedFile(name, file.read(), content_type='image/jpeg')


class EcommerceAPITestCase(APITestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(
            email='testuser@example.com', 
            password='password123', 
            first_name='Test', 
            last_name='User', 
            phone='+2348012345678'
        )
        self.user2 = User.objects.create_user(
            email='testuser2@example.com', 
            password='password123', 
            first_name='Test', 
            last_name='User2', 
            phone='+2348012345679'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        # Create category and type
        self.category = ProductsCategory.objects.create(name='Male', color='blue')
        self.type = ProductsType.objects.create(name='Shirt', color='green')

        # Product data
        self.product_data = {
            'name': 'Test Shirt',
            'category_id': self.category.id,
            'type_id': self.type.id,
            'package_type': 'single',
            'price': '2000.00',
            'discount_type': 'percent',
            'discount_value': '10',
            'currency': 'NGN',
            'description': 'A test shirt',
            'quantity': 5
        }

    # ---------------------
    # Product CRUD
    # ---------------------
    def test_create_product_with_images(self):
        url = reverse('product-list-create') 
        images = [get_test_image(f'image{i}.jpg') for i in range(3)]
        data = self.product_data.copy()
        data['images'] = images

        response = self.client.post(url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Product.objects.count(), 1)
        product = Product.objects.first()
        self.assertEqual(product.images.count(), 3)
        self.assertTrue(product.images.filter(is_primary=True).exists())

    def test_get_product_list(self):
        Product.objects.create(**self.product_data)
        url = reverse('product-list-create')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('data', response.data)

    def test_get_product_detail(self):
        product = Product.objects.create(**self.product_data)
        url = reverse('product-detail', kwargs={'pk': product.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data']['name'], product.name)

    def test_update_product(self):
        product = Product.objects.create(**self.product_data)
        url = reverse('product-detail', kwargs={'pk': product.id})

        response = self.client.put(url, {'name': 'Updated Shirt'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        product.refresh_from_db()
        self.assertEqual(product.name, 'Updated Shirt')

    def test_delete_product(self):
        product = Product.objects.create(**self.product_data)
        url = reverse('product-detail', kwargs={'pk': product.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Product.objects.count(), 0)

    # ---------------------
    # Review Tests
    # ---------------------
    def test_create_review_for_product(self):
        product = Product.objects.create(**self.product_data)
        url = reverse('review-detail', kwargs={'product_id': str(product.id)})
        data = {'rating': 4, 'comment': 'Good product'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Review.objects.count(), 1)
        review = Review.objects.first()
        self.assertEqual(review.user, self.user)
        self.assertEqual(review.product, product)

    def test_get_user_reviews(self):
        product = Product.objects.create(**self.product_data)
        Review.objects.create(product=product, user=self.user, rating=5)
        url = reverse('review-detail', kwargs={'product_id': product.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']), 1)
        self.assertEqual(response.data['data'][0]['rating'], 5)

    def test_review_score_property(self):
        product = Product.objects.create(**self.product_data)
        Review.objects.create(product=product, user=self.user, rating=5)
        Review.objects.create(product=product, user=self.user2, rating=4)
        self.assertEqual(product.review_score, 4.5)

