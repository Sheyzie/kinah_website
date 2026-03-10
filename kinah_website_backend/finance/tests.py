from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth import get_user_model
from products.models import Product, ProductsCategory, ProductsType
from .models import Address, Order, OrderStatusHistory, Payment, Coupon
import json
from decimal import Decimal
from datetime import datetime
import uuid


User = get_user_model()


class DecimalDatetimeUUIDEncoder(json.JSONEncoder):
    '''
    Class to parse Decimal object
    '''
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        if isinstance(obj, uuid.UUID) or isinstance(obj, datetime):
            return str(obj)
        return super().default(obj)


def printResult(data):
    print(json.dumps(data, indent=3, cls=DecimalDatetimeUUIDEncoder))


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
        product_data = {
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

        self.product = Product.objects.create(**product_data)

        # Address data
        self.address_data = {
            "address_type": "shipping",
            "full_name": "John Doe",
            "street_address": "123 Main St",
            "city": "Lagos",
            "state": "Lagos",
            "country": "Nigeria"
        }

        # Order data
        self.order_data = {
            "payment_method": "paystack",
            "items": [
                {
                    "product": self.product.id,
                    "quantity": 2,
                    "unit_price": "100.00"
                }
            ]
        }

        # Coupon data
        self.coupon_data = {
            'code': "TEST10",
            'discount_type': "percent",
            'discount_value': 10,
            'valid_from': timezone.now(),
            'valid_to': timezone.now() + timezone.timedelta(days=1),
            'is_active': True
        }

    # ---------------------
    # Address CRUD
    # ---------------------
    def test_create_address(self):
        url = reverse('address-list')
        data = self.address_data

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Address.objects.count(), 1)

    def test_get_addresses(self):
        address = Address.objects.create(user=self.user, **self.address_data)
        url = reverse('address-detail', kwargs={'pk': address.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('data', response.data)

    def test_update_address(self):
        address = Address.objects.create(user=self.user, **self.address_data)
        url = reverse('address-detail', kwargs={'pk': address.id})

        data = {
            "address_type": "billing",
            "full_name": "John Doe",
            "street_address": "123 Main St",
            "city": "Abuja",
            "state": "Lagos",
            "country": "Nigeria"
        }

        response = self.client.put(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        address.refresh_from_db()
        self.assertEqual(address.city, 'Abuja')
        self.assertEqual(address.address_type, 'billing')

    def test_delete_address(self):
        address = Address.objects.create(user=self.user, **self.address_data)
        url = reverse('address-detail', kwargs={'pk': address.id})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Address.objects.count(), 0)


    # ---------------------
    # Order Tests
    # ---------------------
    def test_create_order(self):
        url = reverse('order-list')
        data = self.order_data
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Order.objects.count(), 1)

    def test_list_orders(self):
        Order.objects.create(
            user=self.user,
            payment_method="paystack",
            order_number="ORD-001"
        )
        url = reverse('order-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('data', response.data)

    def test_get_order_detail(self):
        order = Order.objects.create(
            user=self.user,
            payment_method="paystack",
            order_number="ORD-001"
        )
        url = reverse('order-detail', kwargs={'pk': order.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('data', response.data)

    def test_unauthorised_update_order(self):
        order = Order.objects.create(
            user=self.user,
            payment_method="paystack",
            order_number="ORD-001",
            status='processing'
        )
        url = reverse('order-detail', kwargs={'pk': order.id})

        data = {
            "payment_method": "credit_card",
            "items": [
                {
                    "product": self.product.id,
                    "quantity": 2,
                    "unit_price": "100.00"
                }
            ]
        }

        response = self.client.put(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        order.refresh_from_db()
        self.assertEqual(order.payment_method, 'paystack')

    def test_authorised_update_order(self):
        admin_user = User.objects.create_superuser(
            email='superUser@example.com', 
            password='password123', 
            first_name='Admin', 
            last_name='User', 
            phone='+2348012345699'
        )

        self.client = APIClient()
        self.client.force_authenticate(user=admin_user)

        order = Order.objects.create(
            user=admin_user,
            payment_method="paystack",
            order_number="ORD-001",
            status='processing'
        )
        url = reverse('order-detail', kwargs={'pk': order.id})

        data = {
            "payment_method": "credit_card",
            "items": [
                {
                    "product": self.product.id,
                    "quantity": 2,
                    "unit_price": "100.00"
                }
            ]
        }

        response = self.client.put(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        order.refresh_from_db()
        self.assertEqual(order.payment_method, 'credit_card')

    def test_update_order_status(self):
        admin_user = User.objects.create_superuser(
            email='superUser@example.com', 
            password='password123', 
            first_name='Admin', 
            last_name='User', 
            phone='+2348012345699'
        )

        self.client = APIClient()
        self.client.force_authenticate(user=admin_user)

        order = Order.objects.create(
            user=admin_user,
            payment_method="paystack",
            order_number="ORD-001",
            status='pending'
        )
        url = reverse('order-detail', kwargs={'pk': order.id})
        url = url + 'update_status/'

        data = {
            "payment_method": "credit_card",
            'status': 'processing',
            "items": [
                {
                    "product": self.product.id,
                    "quantity": 2,
                    "unit_price": "100.00"
                }
            ]
        }

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        order.refresh_from_db()
        self.assertEqual(order.status, 'processing')
        self.assertEqual(OrderStatusHistory.objects.count(), 1)

    def test_delete_order(self):
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        order = Order.objects.create(
            user=self.user,
            payment_method="paystack",
            order_number="ORD-001",
            status='processing'
        )
        url = reverse('order-detail', kwargs={'pk': order.id})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Order.objects.count(), 0)


    # ---------------------
    # Payment Tests
    # ---------------------
    def test_create_payment(self):
        url = reverse('order-list')
        data = self.order_data
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Order.objects.count(), 1)

        order = Order.objects.first()

        data = {
            "order": order.id,
            "payment_method": "paystack",
            "amount": 100.00,
            "status": "processing"
        }

        url = reverse('payment-list')
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Payment.objects.count(), 1)
        order.refresh_from_db()

    def test_list_payments(self):
        url = reverse('order-list')
        data = self.order_data
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Order.objects.count(), 1)

        order = Order.objects.first()

        Payment.objects.create(
            order=order,
            payment_method="paystack",
            amount=100,
            status="initiated"
        )
        url = reverse('payment-list')
        response = self.client.get(url)
       
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('data', response.data)

    def test_get_payment_detail(self):
        url = reverse('order-list')
        data = self.order_data
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Order.objects.count(), 1)

        order = Order.objects.first()

        payment = Payment.objects.create(
            order=order,
            payment_method="paystack",
            amount=100,
            status="initiated"
        )

        url = reverse('payment-detail', kwargs={'pk': payment.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('data', response.data)

    def test_unauthorised_update_order(self):
        url = reverse('order-list')
        data = self.order_data
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Order.objects.count(), 1)

        order = Order.objects.first()

        payment = Payment.objects.create(
            order=order,
            payment_method="paystack",
            amount=100,
            status="initiated"
        )

        url = reverse('payment-detail', kwargs={'pk': payment.id})

        data = {
            "order": order.id,
            "payment_method": "credit_card",
            "amount": "100.00",
            "status": "paid"
        }

        response = self.client.put(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        payment.refresh_from_db()
        self.assertEqual(payment.payment_method, 'paystack')

    def test_authorised_update_order(self):
        admin_user = User.objects.create_superuser(
            email='superUser@example.com', 
            password='password123', 
            first_name='Admin', 
            last_name='User', 
            phone='+2348012345655'
        )

        url = reverse('order-list')
        data = self.order_data
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Order.objects.count(), 1)

        order = Order.objects.first()

        self.client = APIClient()
        self.client.force_authenticate(user=admin_user)

        payment = Payment.objects.create(
            order=order,
            payment_method="paystack",
            amount=100,
            status="initiated"
        )

        url = reverse('payment-detail', kwargs={'pk': payment.id})

        data = {
            "order": order.id,
            "payment_method": "credit_card",
            "amount": 100.00,
            "status": "completed"
        }

        response = self.client.put(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        payment.refresh_from_db()
        payment.status = 'completed'
        payment.save()
        self.assertEqual(payment.payment_method, 'credit_card')
        order.refresh_from_db()
        self.assertNotEqual(order.payment_status, 'pending')

    def test_delete_payment(self):
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        url = reverse('order-list')
        data = self.order_data
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Order.objects.count(), 1)

        order = Order.objects.first()

        payment = Payment.objects.create(
            order=order,
            payment_method="paystack",
            amount=100,
            status="initiated"
        )

        url = reverse('payment-detail', kwargs={'pk': payment.id})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Payment.objects.count(), 0)

    # ---------------------
    # Coupon Tests
    # ---------------------
    def test_create_coupon(self):
        admin_user = User.objects.create_superuser(
            email='superUser@example.com', 
            password='password123', 
            first_name='Admin', 
            last_name='User', 
            phone='+2348012345655'
        )

        self.client = APIClient()
        self.client.force_authenticate(user=admin_user)

        url = reverse('coupon-list')
        data = self.coupon_data
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Coupon.objects.count(), 1)

    def test_list_coupon(self):
        admin_user = User.objects.create_superuser(
            email='superUser@example.com', 
            password='password123', 
            first_name='Admin', 
            last_name='User', 
            phone='+2348012345655'
        )

        self.client = APIClient()
        self.client.force_authenticate(user=admin_user)

        Coupon.objects.create(**self.coupon_data)
        url = reverse('coupon-list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('data', response.data)

    def test_get_coupon_detail(self):
        admin_user = User.objects.create_superuser(
            email='superUser@example.com', 
            password='password123', 
            first_name='Admin', 
            last_name='User', 
            phone='+2348012345655'
        )

        self.client = APIClient()
        self.client.force_authenticate(user=admin_user)

        coupon = Coupon.objects.create(**self.coupon_data)
        url = reverse('coupon-detail', kwargs={'pk': coupon.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('data', response.data)

    def test_unauthorised_update_coupon(self):
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        coupon = Coupon.objects.create(**self.coupon_data)
        url = reverse('coupon-detail', kwargs={'pk': coupon.id})

        data = {
            'code': "TEST11",
            'discount_type': "percent",
            'discount_value': 10,
            'valid_from': timezone.now(),
            'valid_to': timezone.now() + timezone.timedelta(days=1),
            'is_active': True
        }

        response = self.client.put(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        coupon.refresh_from_db()
        self.assertEqual(coupon.code, 'TEST10')

    def test_authorised_update_coupon(self):
        admin_user = User.objects.create_superuser(
            email='superUser@example.com', 
            password='password123', 
            first_name='Admin', 
            last_name='User', 
            phone='+2348012345655'
        )

        self.client = APIClient()
        self.client.force_authenticate(user=admin_user)

        coupon = Coupon.objects.create(**self.coupon_data)
        url = reverse('coupon-detail', kwargs={'pk': coupon.id})

        data = {
            'code': "TEST11",
            'discount_type': "percent",
            'discount_value': 10,
            'valid_from': timezone.now(),
            'valid_to': timezone.now() + timezone.timedelta(days=1),
            'is_active': True
        }

        response = self.client.put(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        coupon.refresh_from_db()
        self.assertEqual(coupon.code, 'TEST11')

    def test_delete_payment(self):
        admin_user = User.objects.create_superuser(
            email='superUser@example.com', 
            password='password123', 
            first_name='Admin', 
            last_name='User', 
            phone='+2348012345655'
        )

        self.client = APIClient()
        self.client.force_authenticate(user=admin_user)

        coupon = Coupon.objects.create(**self.coupon_data)
        url = reverse('coupon-detail', kwargs={'pk': coupon.id})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Payment.objects.count(), 0)

    def test_validate_coupon(self):
        admin_user = User.objects.create_superuser(
            email='superUser@example.com', 
            password='password123', 
            first_name='Admin', 
            last_name='User', 
            phone='+2348012345655'
        )

        self.client = APIClient()
        self.client.force_authenticate(user=admin_user)

        coupon = Coupon.objects.create(**self.coupon_data)

        data = {
            "code": "TEST10",
            "subtotal": 200
        }
        url = reverse('coupon-list')
        url = url + 'validate_coupon/'
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        coupon.refresh_from_db()
        self.assertIn('data', response.data)



