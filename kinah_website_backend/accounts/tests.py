from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.hashers import make_password
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from django.core import mail
from unittest.mock import patch, MagicMock

from finance.models import Order
from .utils import printInJSON

from .test_data import ROLE_DATA, USER_DATA, USER_PASSWORD_DATA, ROLE_PERMISSION_DATA
from .models import Role, RolePermission, OTPRecord


User = get_user_model()

# Test:
#   1. Role:
#       - Create a role via API
#       - Get a role via API
#       - Update a role via API
#       - Delete a role via API
#   2. User: 
#       - Register a user via API end point 
#       - Get user details via API end point
#       - Update a user via API end point
#       - Set user login via API
#       - Login as user via API
#       - Delete a user via API end point
#   3. RolePermission: 
#       - Create a role permission via API end point 
#       - Get role permission details via API end point
#       - Update a role permission via API end point
#       - Delete a role permission via API end point

# color='#54fa72',
# color="#f462b3",


class BaseAPITest(APITestCase):
    def get_auth_token(self, email=None, password=None):
        # get access and refresh token
        url = reverse('token_obtain_pair')
        data = {
            'email': email,
            'password': password
        }
        
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertIsNotNone(response.data['access'])
        self.assertIsNotNone(response.data['refresh'])

        return response.data['access']


class RoleAPITestCase(BaseAPITest):
    def setUp(self):
        # createsuperuser
        superuser = USER_DATA.get('superuser')
        user = USER_DATA.get('register')
        self.superadmin = User.objects.create_superuser(
            password='superAdminUser',
            **superuser
        )

        self.user = User.objects.create_user(
            password='justUser',
            **user
        )

    def test_create_role(self):

        token = self.get_auth_token(
            email=self.superadmin.email,
            password='superAdminUser'
        )

        headers = {
            'Authorization': f'Bearer {token}'
        }

        url = reverse('roles-list')
        data = ROLE_DATA["create"]
        response = self.client.post(url, data, headers=headers, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('data', response.data)
        self.assertGreater(Role.objects.count(), 0)

    def test_get_role(self):
        # get token
        token = self.get_auth_token(
            email=self.superadmin.email,
            password='superAdminUser'
        )

        headers = {
            'Authorization': f'Bearer {token}'
        }

        # create role
        role = Role.objects.create(**ROLE_DATA["create"])

        # test GET
        url = reverse('roles-detail', kwargs={'pk': role.id})
        response = self.client.get(url, headers=headers,)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data']["role_name"], role.role_name)

    def test_update_role(self):
        # get token
        token = self.get_auth_token(
            email=self.superadmin.email,
            password='superAdminUser'
        )

        headers = {
            'Authorization': f'Bearer {token}'
        }
        
        # create role
        role = Role.objects.create(**ROLE_DATA["create"])

        # update
        url = reverse('roles-detail', kwargs={'pk': role.id})
        updated_data = ROLE_DATA["update"]
        response = self.client.put(url, updated_data, headers=headers, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data']["role_name"], updated_data["role_name"])
        self.assertNotEqual(response.data['data']["role_name"], role.role_name)

    def test_update_non_editable_role(self):
        # get token
        token = self.get_auth_token(
            email=self.superadmin.email,
            password='superAdminUser'
        )

        headers = {
            'Authorization': f'Bearer {token}'
        }
        
        # create role
        role = Role.objects.create(**ROLE_DATA["create"])

        token = self.get_auth_token(
            email=self.user.email,
            password='justUser'
        )

        headers = {
            'Authorization': f'Bearer {token}'
        }

        # update
        url = reverse('roles-detail', kwargs={'pk': role.id})
        updated_data = ROLE_DATA["update"]
        updated_data['is_editable'] = False

        response = self.client.put(url, updated_data, headers=headers, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_role(self):
        # get token
        token = self.get_auth_token(
            email=self.superadmin.email,
            password='superAdminUser'
        )

        headers = {
            'Authorization': f'Bearer {token}'
        }

        # create role
        role = Role.objects.create(**ROLE_DATA["create"])

        # delete
        url = reverse('roles-detail', kwargs={'pk': role.id})
        response = self.client.delete(url, headers=headers)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # confirm deletion
        get_response = self.client.get(url, headers=headers)

        self.assertEqual(get_response.status_code, status.HTTP_404_NOT_FOUND)


class UserAPITestCase(BaseAPITest):
    def setUp(self):
        # createsuperuser
        superuser = USER_DATA.get('superuser')
        superuser['password'] = 'superAdminUser'
        self.superadmin = User.objects.create_superuser(
            **superuser
        )

        user_data = USER_DATA.get('register')
        user_data['password'] = 'John6b4pt15t'
        self.user = User.objects.create_user(
            **user_data
        )

        token = self.get_auth_token(
            email=self.superadmin.email,
            password='superAdminUser'
        )

        headers = {
            'Authorization': f'Bearer {token}'
        }
        
        # create role
        self.role = Role.objects.create(**ROLE_DATA["create"])

    def test_register_user(self):
        token = self.get_auth_token(
            email=self.superadmin.email,
            password='superAdminUser'
        )

        headers = {
            'Authorization': f'Bearer {token}'
        }

        url = reverse('users-list')
        data = USER_DATA["register"].copy()
        data['password'] = 'John6b4pt15t'
        data['email'] = 'new@msil.com'
        data['phone'] = '+2348112312345'

        # pass in role_id
        data['role_id'] = self.role.id

        response = self.client.post(url, data, headers=headers, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        user = User.objects.get(email=USER_DATA["register"]['email'])
        self.assertEqual(user.first_name, data['first_name'])

        # check role 
        self.assertEqual(user.role.role_name, 'buyer')

        # check default permissions
        self.assertGreater(RolePermission.objects.count(), 0)

    def test_get_users(self):
        # log in as super admin
        token = self.get_auth_token(
            email=self.superadmin.email,
            password='superAdminUser'
        )

        headers = {
            'Authorization': f'Bearer {token}'
        }

        # fetch users
        url = reverse('users-list')
        response = self.client.get(url, headers=headers)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotEqual(response.data['data']['count'], 0)

    def test_update_user(self):

        # log in as super admin
        token = self.get_auth_token(
            email=self.superadmin.email,
            password='superAdminUser'
        )

        headers = {
            'Authorization': f'Bearer {token}'
        }

        url = reverse('users-detail', kwargs={'pk': self.user.id})
        updated_data = USER_DATA["update"]
        updated_data['role_id'] = self.role.id

        response = self.client.put(url, updated_data, headers=headers, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotEqual(response.data["data"]['first_name'], self.user.first_name)
   
    def test_set_user_login(self):
        # log in as super admin
        token = self.get_auth_token(
            email=self.superadmin.email,
            password='superAdminUser'
        )

        headers = {
            'Authorization': f'Bearer {token}'
        }

        # password reset info
        user_password_reset = USER_PASSWORD_DATA['set_password']
        user_password_reset['uidb64'] = urlsafe_base64_encode(force_bytes(self.user.id))
        user_password_reset['token'] = default_token_generator.make_token(self.user)

        url = reverse('set_password')
        response = self.client.post(url, user_password_reset, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_login_user(self):
        # log in as super admin
        token = self.get_auth_token(
            email=self.superadmin.email,
            password='superAdminUser'
        )

        headers = {
            'Authorization': f'Bearer {token}'
        }

        # activate user
        url = reverse('users-detail', kwargs={'pk': self.user.id}) + 'activate/'
        response = self.client.get(url, headers=headers, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # password reset info
        user_password_reset = USER_PASSWORD_DATA['set_password']
        user_password_reset['uidb64'] = urlsafe_base64_encode(force_bytes(self.user.id))
        user_password_reset['token'] = default_token_generator.make_token(self.user)

        url = reverse('set_password')
        response = self.client.post(url, user_password_reset, format='json')

        url = reverse('token_obtain_pair')
        response = self.client.post(url, USER_DATA["login"], format='json') 

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)

    def test_delete_user(self):
        # log in as super admin
        token = self.get_auth_token(
            email=self.superadmin.email,
            password='superAdminUser'
        )
        headers = {
            'Authorization': f'Bearer {token}'
        }

        # delete
        url = reverse('users-detail', kwargs={'pk': self.user.id})
        response = self.client.delete(url, headers=headers)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # # confirm deletion
        get_response = self.client.get(url, headers=headers)
        self.assertEqual(get_response.status_code, status.HTTP_404_NOT_FOUND)

    def test_verify_user(self):
        # log in as super admin
        token = self.get_auth_token(
            email=self.superadmin.email,
            password='superAdminUser'
        )

        headers = {
            'Authorization': f'Bearer {token}'
        }

        # password reset info
        uidb64 = urlsafe_base64_encode(force_bytes(self.user.id))
        token = default_token_generator.make_token(self.user)
        
        data = {
            'uidb64': uidb64,
            'token': token,
            'otp': '123456'
        }

        otp = OTPRecord.objects.create(
            otp=make_password('123456'),
            user=self.user,
            event='verify'
        )

        url = reverse('users-list') + 'verify_user/'
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_active)

    def test_get_user_profile(self):
        # log in as user
        token = self.get_auth_token(
            email=self.user.email,
            password='John6b4pt15t'
        )

        headers = {
            'Authorization': f'Bearer {token}'
        }

        order = Order.objects.create(
            user=self.user,
            payment_method="paystack",
            order_number="ORD-001",
            status='processing',
            customer_email=self.user.email
        )

        url = reverse('users-list') + 'me/'
        response = self.client.get(url, headers=headers)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_active)

    def test_register_staff_user(self):
        token = self.get_auth_token(
            email=self.superadmin.email,
            password='superAdminUser'
        )

        headers = {
            'Authorization': f'Bearer {token}'
        }

        url = reverse('users-list') + 'create_staff/'
        data = USER_DATA["register"].copy()
        data['password'] = 'John6b4pt15t'
        data['email'] = 'staff@mail.com'
        data['phone'] = '+2348156341122'

        # pass in role_id
        data['role_id'] = self.role.id

        # staff address
        data['address'] = {
            'full_name': 'Test Staff', 
            'street_address': '123 Main st', 
            'apartment_address': 'Block B', 
            'city': 'Ikeja', 
            'state': 'Lagos',
            'postal_code': '100262',
            'country': 'Nigeria'
        }

        response = self.client.post(url, data, headers=headers, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        user = User.objects.get(email='staff@mail.com')
        self.assertEqual(user.first_name, data['first_name'])

        # check role 
        user.refresh_from_db()
        self.assertEqual(user.role.role_name, 'staff')

        # check default permissions
        self.assertGreater(RolePermission.objects.count(), 0)


class RolePermissionAPITestCase(BaseAPITest):

    def setUp(self):

        # createsuperuser
        superuser = USER_DATA.get('superuser')

        self.superadmin = User.objects.create_superuser(
            first_name=superuser['first_name'],
            last_name=superuser['last_name'],
            email=superuser['email'],
            phone=superuser['phone'],
            password='superAdminUser'
        )

        # create real Role
        self.role = Role.objects.create(
            role_name="Manager",
            color="#123456",
            is_admin=False,
            is_editable=True,
            is_default=False,
            is_active=False
        )

        # pick a ContentType (any real model)
        self.content_type = ContentType.objects.get_for_model(Role)

        # update data IDs dynamically
        role_permission_create = ROLE_PERMISSION_DATA["create"].copy()
        role_permission_update = ROLE_PERMISSION_DATA["update"].copy()
        role_permission_create["role_id"] = self.role.id
        role_permission_create["content_type_id"] = self.content_type.id

        role_permission_update["role_id"] = self.role.id
        role_permission_update["content_type_id"] = self.content_type.id

        self.list_url = reverse('roleperms-list')

    def test_create_role_permission(self):
        token = self.get_auth_token(
            email=self.superadmin.email,
            password='superAdminUser'
        )

        headers = {
            'Authorization': f'Bearer {token}'
        }

        data = ROLE_PERMISSION_DATA["create"].copy()
        data['content_type_ids'] = [self.content_type.id]

        response = self.client.post(
            self.list_url,
            data,
            headers=headers,
            format="json"
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # validate read-only fields present
        self.assertIn("role", response.data['data'])
        self.assertIn("content_type", response.data['data'])

        # validate flag values
        self.assertTrue(response.data['data']["can_create"])
        self.assertTrue(response.data['data']["can_read"])

    def test_get_role_permission(self):
        token = self.get_auth_token(
            email=self.superadmin.email,
            password='superAdminUser'
        )

        headers = {
            'Authorization': f'Bearer {token}'
        }

        # create first
        roleperm = RolePermission.objects.create(content_type=self.content_type, **ROLE_PERMISSION_DATA["create"])

        url = reverse('roleperms-detail', kwargs={'pk': roleperm.id})
        response = self.client.get(url, headers=headers)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data']["role"], roleperm.role.role_name)

    def test_update_role_permission(self):
        token = self.get_auth_token(
            email=self.superadmin.email,
            password='superAdminUser'
        )

        headers = {
            'Authorization': f'Bearer {token}'
        }

        # create first
        roleperm = RolePermission.objects.create(content_type=self.content_type, **ROLE_PERMISSION_DATA["create"])

        url = reverse('roleperms-detail', kwargs={'pk': roleperm.id})
        data = ROLE_PERMISSION_DATA["update"]
        data['content_type_ids'] = [self.content_type.id]
        response = self.client.put(
            url,
            ROLE_PERMISSION_DATA["update"],
            headers=headers,
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['data']["can_delete"])
        self.assertTrue(response.data['data']["can_manage"])
        self.assertTrue(response.data['data']["can_update"])
        self.assertTrue(response.data['data']["can_dispatch_driver"])

    def test_delete_role_permission(self):
        token = self.get_auth_token(
            email=self.superadmin.email,
            password='superAdminUser'
        )

        headers = {
            'Authorization': f'Bearer {token}'
        }

        # create first
        roleperm = RolePermission.objects.create(content_type=self.content_type, **ROLE_PERMISSION_DATA["create"])

        url = reverse('roleperms-detail', kwargs={'pk': roleperm.id})
        response = self.client.delete(url, headers=headers)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # confirm deletion
        get_response = self.client.get(url, headers=headers)
        self.assertEqual(get_response.status_code, status.HTTP_404_NOT_FOUND)

    def test_unique_constraint(self):
        token = self.get_auth_token(
            email=self.superadmin.email,
            password='superAdminUser'
        )

        headers = {
            'Authorization': f'Bearer {token}'
        }
        data = ROLE_PERMISSION_DATA["create"].copy()
        data['content_type_ids'] = [self.content_type.id]

        # create first instance
        self.client.post(
            self.list_url,
            data,
            headers=headers,
            format="json"
        )

        # attempt to create duplicate role + content_type pair
        response = self.client.post(
            self.list_url,
            data,
            headers=headers,
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Double entry for permission", response.data)

    def test_get_content_types(self):
        url = reverse('content_types')
        token = self.get_auth_token(
            email=self.superadmin.email,
            password='superAdminUser'
        )

        headers = {
            'Authorization': f'Bearer {token}'
        }

        resp = self.client.get(url, headers=headers)

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertGreater(len(resp.data['data']), 0)


class APIThrottlingTest(BaseAPITest):
    def setUp(self):
        # createsuperuser
        superuser = USER_DATA.get('superuser')

        self.superadmin = User.objects.create_superuser(
            first_name=superuser['first_name'],
            last_name=superuser['last_name'],
            email=superuser['email'],
            phone=superuser['phone'],
            password='superAdminUser'
        )

    def test_anon_throttling(self):
        '''Test Anonymouse throttling at 20/min'''
        url = reverse('password_reset')

        data = {
            'email': "rate@mail.come",
            'password': 'ratePass'
        }

        response = None
        rate = 0
        for i in range(22):
            rate = i + 1
            response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)
        
    # "login": "5/min",
    # "user": "100/min",
    

class AuthenticationTestCase(BaseAPITest):
    """Test suite for authentication flow"""

    def setUp(self):
        """Set up test data"""
        self.client = APIClient()

        role = Role.objects.create(
            role_name="user",
            color="#C28383",
            is_admin=False,
            is_editable=True,
            is_default=False,
            is_active=True
        )

        content_type = ContentType.objects.get_for_model(User)

        role_perm = RolePermission.objects.create(
            role=role,
            content_type=content_type,
            can_create=False,
            can_read=True,
            can_update=False,
            can_delete=False,
            can_manage=False,
            can_create_account=False,
            can_dispatch_driver=False
        )
        
        # Create test user
        self.user_data = {
            'email': 'test@mzansilogistic.com',
            'first_name': 'Test',
            'last_name': 'User',
            'phone': '+254712345678',
        }

        self.password = 'TestPassword123!'
        
        self.user = User.objects.create_user(
            **self.user_data,
            password=self.password,
            role=role
        )

    def test_01_login_success(self):
        """Test successful login with valid credentials"""
        url = reverse('token_obtain_pair')
        data = {
            'email': self.user_data['email'],
            'password': self.password
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertIsNotNone(response.data['access'])
        self.assertIsNotNone(response.data['refresh'])

    def test_02_login_invalid_email(self):
        """Test login with invalid email"""
        url = reverse('token_obtain_pair')
        data = {
            'email': 'wrong@mzansilogistic.com',
            'password': self.password
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_03_login_invalid_password(self):
        """Test login with invalid password"""
        url = reverse('token_obtain_pair')
        data = {
            'email': self.user_data['email'],
            'password': 'WrongPassword123!'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_04_login_missing_fields(self):
        """Test login with missing fields"""
        url = reverse('token_obtain_pair')
        
        # Missing password
        response = self.client.post(url, {'email': self.user_data['email']}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Missing email
        response = self.client.post(url, {'password': self.password}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_05_token_refresh_success(self):
        """Test successful token refresh"""
        # First, login to get tokens
        login_url = reverse('token_obtain_pair')
        login_data = {
            'email': self.user_data['email'],
            'password': self.password
        }
        login_response = self.client.post(login_url, login_data, format='json')
        refresh_token = login_response.data['refresh']
        
        # Now refresh the token
        refresh_url = reverse('token_refresh')
        refresh_data = {'refresh': refresh_token}
        response = self.client.post(refresh_url, refresh_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIsNotNone(response.data['access'])
        self.assertIsNotNone(response.data['refresh'])
    
    def test_06_token_refresh_invalid(self):
        """Test token refresh with invalid refresh token"""
        refresh_url = reverse('token_refresh')
        refresh_data = {'refresh': 'invalid_refresh_token'}
        response = self.client.post(refresh_url, refresh_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_07_protected_endpoint_without_token(self):
        """Test accessing protected endpoint without token"""
        url = reverse('users-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_08_protected_endpoint_with_valid_token(self):
        """Test accessing protected endpoint with valid token"""
        # Login to get token
        login_url = reverse('token_obtain_pair')
        login_data = {
            'email': self.user_data['email'],
            'password': self.password
        }
        login_response = self.client.post(login_url, login_data, format='json')
        access_token = login_response.data['access']
        
        # Access protected endpoint
        url = reverse('users-list')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_09_password_reset_request(self):
        """Test password reset request"""
        url = reverse('password_reset')
        data = {
            'account': self.user_data['email'],
            'email': self.user_data['email']
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['status'])
        
        # Check that email was sent (UNCOMMENT after setting up Email Service)
        # self.assertEqual(len(mail.outbox), 1)
        # self.assertIn('MzansiLogistics Password', mail.outbox[0].subject)

    def test_10_password_reset_invalid_email(self):
        """Test password reset with non-existent email"""
        url = reverse('password_reset')
        data = {
            'account': 'nonexistent',
            'email': 'nonexistent@cargopal.com'
        }
        
        response = self.client.post(url, data, format='json')
        
        # Should return 200 for security (don't reveal if email exists)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # But no email should be sent
        self.assertEqual(len(mail.outbox), 0)

    def test_11_set_password_success(self):
        """Test setting new password with valid token"""
        # Generate valid token
        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        token = default_token_generator.make_token(self.user)
        
        url = reverse('set_password')
        data = {
            'uidb64': uid,
            'token': token,
            'new_password': 'NewPassword123!'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify new password works
        login_url = reverse('token_obtain_pair')
        login_data = {
            'email': self.user_data['email'],
            'password': 'NewPassword123!'
        }
        login_response = self.client.post(login_url, login_data, format='json')
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)

    def test_12_set_password_invalid_token(self):
        """Test setting password with invalid token"""
        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        
        url = reverse('set_password')
        data = {
            'uidb64': uid,
            'token': 'invalid_token',
            'new_password': 'NewPassword123!'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_13_set_password_weak_password(self):
        """Test setting weak password"""
        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        token = default_token_generator.make_token(self.user)
        
        url = reverse('set_password')
        data = {
            'uidb64': uid,
            'token': token,
            'new_password': '123'  # Too weak
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_14_inactive_user_cannot_login(self):
        """Test that inactive users cannot login"""
        # Deactivate user
        self.user.is_active = False
        self.user.save()
        
        url = reverse('token_obtain_pair')
        data = {
            'email': self.user_data['email'],
            'password': self.password
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_15_concurrent_logins(self):
        """Test multiple concurrent logins (tokens)"""
        url = reverse('token_obtain_pair')
        data = {
            'email': self.user_data['email'],
            'password': self.password
        }
        
        # Get first token
        response1 = self.client.post(url, data, format='json')
        token1 = response1.data['access']
        
        # Get second token
        response2 = self.client.post(url, data, format='json')
        token2 = response2.data['access']
        
        # Both tokens should be valid and different
        self.assertNotEqual(token1, token2)
        
        # Both should work for protected endpoints
        protected_url = reverse('users-list')
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token1}')
        response = self.client.get(protected_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token2}')
        response = self.client.get(protected_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class RoleBasedAccessTestCase(BaseAPITest):
    """Test suite for role-based access control"""

    def setUp(self):
        """Set up test data with different roles"""
        content_type = ContentType.objects.get_for_model(User)
     
        # Create roles
        self.admin_role = Role.objects.create(
            role_name='Admin',
            color='#FF0000',
            is_admin=True
        )
        
        self.user_role = Role.objects.create(
            role_name='User',
            color='#0000FF',
            is_admin=False
        )

        role_perm = RolePermission.objects.create(
            role=self.user_role,
            content_type=content_type,
            can_create=False,
            can_read=True,
            can_update=False,
            can_delete=False,
            can_manage=False,
            can_create_account=False,
            can_dispatch_driver=False
        )
        
        # Create admin user
        self.admin_user = User.objects.create_user(
            email='admin@mzansilogistic.org',
            first_name='Admin',
            last_name='User',
            phone='+254712345601',
            password='AdminPass123!',
            role=self.admin_role
        )
        
        # Create regular user
        self.regular_user = User.objects.create_user(
            email='user@mzansilogistic.org',
            first_name='Regular',
            last_name='User',
            phone='+254712345602',
            password='UserPass123!',
            role=self.user_role
        )

    def test_admin_access(self):
        """Test admin can access admin endpoints"""
        token = self.get_auth_token('admin@mzansilogistic.org', 'AdminPass123!')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

        url = reverse('roles-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_regular_user_access(self):
        """Test regular user cannot access their own role"""
        token = self.get_auth_token('user@mzansilogistic.org', 'UserPass123!')
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        url = reverse('roles-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

