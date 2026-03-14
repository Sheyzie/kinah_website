from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model
from finance.models import Address
from accounts.utils import printInJSON
from .models import Vehicle, Dispatch


User = get_user_model()


class EcommerceAPITestCase(APITestCase):
    def setUp(self):
        # Create a test user
        self.admin_user = User.objects.create_superuser(
            email='testuser@example.com', 
            password='password123', 
            first_name='Test', 
            last_name='User', 
            phone='+2348012345678'
        )
        self.user = User.objects.create_user(
            email='testuser2@example.com', 
            password='password123', 
            first_name='Test', 
            last_name='User2', 
            phone='+2348012345679'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.admin_user)

        # Vehicle data
        self.vehicle_data = {
            'vehicle_type': 'Car',
            'vehicle_brand': 'Lambo',
            'plate_number': 'TXT-132-AA',
            'plate_state': 'Lagos',
            'plate_country': 'Nigeria',
            'color': 'red',
        }

        # Dispatch data
        self.dispatch_data = {
            "driver": {
                    'first_name': 'Test', 
                    'last_name': 'Driver', 
                    'email': 'testdriver@mail.com',
                    'password': 'testDriverPass',
                    'phone': '+1234567120'
                },
            "company_address": {
                    'full_name': 'Test Driver', 
                    'street_address': '123 Main st', 
                    'apartment_address': 'Block B', 
                    'city': 'Ikeja', 
                    'state': 'Lagos',
                    'postal_code': '100262',
                    'country': 'Nigeria'
                },
            "vehicle": self.vehicle_data,
            "company_name": 'Test Driver Corp'
        }

    # ---------------------
    # Vehicle CRUD
    # ---------------------
    def test_create_vehicle(self):
        url = reverse('vehicle-list')
        data = self.vehicle_data

        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Vehicle.objects.count(), 1)

    def test_get_vehicles(self):
        vehicle = Vehicle.objects.create(**self.vehicle_data)
        url = reverse('vehicle-detail', kwargs={'pk': vehicle.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('data', response.data)

    def test_update_vehicle(self):
        vehicle = Vehicle.objects.create(**self.vehicle_data)
        url = reverse('vehicle-detail', kwargs={'pk': vehicle.id})

        data = {
            'vehicle_type': 'Car',
            'vehicle_brand': 'Ferrari',
            'plate_number': 'TXT-132-AA',
            'plate_state': 'Lagos',
            'plate_country': 'Nigeria',
            'color': 'black',
        }

        response = self.client.put(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        vehicle.refresh_from_db()
        self.assertEqual(vehicle.vehicle_brand, 'Ferrari')
        self.assertEqual(vehicle.color, 'black')

    def test_delete_vehicle(self):
        vehicle = Vehicle.objects.create(**self.vehicle_data)
        url = reverse('vehicle-detail', kwargs={'pk': vehicle.id})

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Vehicle.objects.count(), 0)

    def test_unathorised_create_vehicle(self):
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        url = reverse('vehicle-list')
        data = self.vehicle_data

        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Vehicle.objects.count(), 0)

    # ---------------------
    # Dispatch CRUD
    # ---------------------
    def test_create_dispatch(self):
        url = reverse('dispatch-list')
        data = self.dispatch_data

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Dispatch.objects.count(), 1)

    def test_get_dispatch(self):
        address = Address.objects.create(**self.dispatch_data['company_address'])
        vehicle = Vehicle.objects.create(**self.vehicle_data)
        dispatch = Dispatch.objects.create(
            driver=self.user, 
            company_address=address, 
            company_name='Test Corp',
            vehicle=vehicle
        )
        url = reverse('dispatch-detail', kwargs={'pk': dispatch.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('data', response.data)

    def test_update_dispatch(self):
        address = Address.objects.create(**self.dispatch_data['company_address'])
        vehicle = Vehicle.objects.create(**self.vehicle_data)
        dispatch = Dispatch.objects.create(
            driver=self.user, 
            company_address=address, 
            company_name='Test Corp',
            vehicle=vehicle
        )
        url = reverse('dispatch-detail', kwargs={'pk': dispatch.id})

        data = self.dispatch_data
        data['vehicle'] = {
                'vehicle_type': 'Car',
                'vehicle_brand': 'Ferrari',
                'plate_number': 'TXT-132-AA',
                'plate_state': 'Lagos',
                'plate_country': 'Nigeria',
                'color': 'black',
            }

        response = self.client.put(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_delete_dispatch(self):
        address = Address.objects.create(**self.dispatch_data['company_address'])
        vehicle = Vehicle.objects.create(**self.vehicle_data)
        dispatch = Dispatch.objects.create(
            driver=self.user, 
            company_address=address, 
            company_name='Test Corp',
            vehicle=vehicle
        )
        url = reverse('dispatch-detail', kwargs={'pk': dispatch.id})

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Dispatch.objects.count(), 0)

    def test_unathorised_create_dispatch(self):
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        url = reverse('dispatch-list')
        data = self.vehicle_data

        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Dispatch.objects.count(), 0)

