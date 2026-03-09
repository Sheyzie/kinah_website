from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from unittest.mock import patch, MagicMock
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import get_user_model
from django.core import mail

from .test_data import ROLE_DATA, USER_DATA, USER_PASSWORD_DATA, ROLE_PERMISSION_DATA
from .models import Role, RolePermission


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


BASE_URL = '/api/v1/'

def printResult(data):
    import json
    print(json.dumps(data, indent=3))

class RoleAPITestCase(APITestCase):
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

    def get_auth_token(self, email=None, password=None):
        # get access and refresh token
        url = BASE_URL + 'token/'
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

    def test_create_role(self):

        token = self.get_auth_token(
            email=self.superadmin.email,
            password='superAdminUser'
        )

        headers = {
            'Authorization': f'Bearer {token}'
        }

        url = BASE_URL + "roles/"
        data = ROLE_DATA["create"]
        response = self.client.post(url, data, headers=headers, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.role_id = response.data.get("id")  # save for later tests

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
        data = ROLE_DATA["create"]
        create_response = self.client.post( BASE_URL + "roles/", data, headers=headers, format='json')
        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)
        
        role_id = create_response.data["id"]

        # test GET
        url = BASE_URL + f"roles/{role_id}/"
        response = self.client.get(url, headers=headers,)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["role_name"], data["role_name"])

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
        created_data = ROLE_DATA["create"]
        create_response = self.client.post(BASE_URL + "roles/", created_data, headers=headers, format='json')
        role_id = create_response.data["id"]

        # update
        url = BASE_URL + f"roles/{role_id}/"
        updated_data = ROLE_DATA["update"]
        response = self.client.put(url, updated_data, headers=headers, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["role_name"], updated_data["role_name"])
        self.assertNotEqual(response.data["role_name"], created_data["role_name"])

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
        created_data = ROLE_DATA["create"]
        create_response = self.client.post(BASE_URL + "roles/", created_data, headers=headers, format='json')

        role_id = create_response.data["id"]

        token = self.get_auth_token(
            email=self.user.email,
            password='justUser'
        )

        headers = {
            'Authorization': f'Bearer {token}'
        }

        # update
        url = BASE_URL + f"roles/{role_id}/"
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
        data = ROLE_DATA["create"]
        create_response = self.client.post(BASE_URL + "roles/", data, headers=headers, format='json')
        role_id = create_response.data["id"]

        # delete
        url = BASE_URL + f"roles/{role_id}/"
        response = self.client.delete(url, headers=headers)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # confirm deletion
        get_response = self.client.get(url, headers=headers)

        self.assertEqual(get_response.status_code, status.HTTP_404_NOT_FOUND)


class UserAPITestCase(APITestCase):
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

        token = self.get_auth_token(
            email=self.superadmin.email,
            password='superAdminUser'
        )

        headers = {
            'Authorization': f'Bearer {token}'
        }
        
        # create role
        url = BASE_URL + "roles/"
        role_data = ROLE_DATA["create"]
        response = self.client.post(url, role_data, headers=headers, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.role_id = response.data['id']


    def get_auth_token(self, email=None, password=None):
        # get access and refresh token
        url = BASE_URL + 'token/'
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

    def test_register_user(self):
        token = self.get_auth_token(
            email=self.superadmin.email,
            password='superAdminUser'
        )

        headers = {
            'Authorization': f'Bearer {token}'
        }

        url = BASE_URL + "users/"
        data = USER_DATA["register"]
        data['password'] = 'John6b4pt15t'

        # pass in role_id
        data['role_id'] = self.role_id

        response = self.client.post(url, data, headers=headers, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        user = User.objects.get(email=USER_DATA["register"]['email'])
        self.assertEqual(user.first_name, data['first_name'])

        # check role 
        self.assertEqual(user.role.role_name, ROLE_DATA['create']['role_name'])

    def test_get_users(self):
        # log in as super admin
        token = self.get_auth_token(
            email=self.superadmin.email,
            password='superAdminUser'
        )

        headers = {
            'Authorization': f'Bearer {token}'
        }

        # create user
        data = USER_DATA["register"]
        data['password'] = 'John6b4pt15t'

        # pass in role_id
        data['role_id'] = self.role_id

        # create a user
        create_response = self.client.post(BASE_URL + "users/", data, headers=headers, format='multipart')
        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)

        # fetch users
        url = BASE_URL + f"users/"
        response = self.client.get(url, headers=headers)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotEqual(len(response.data['results']), 0)

    def test_update_user(self):

        # log in as super admin
        token = self.get_auth_token(
            email=self.superadmin.email,
            password='superAdminUser'
        )

        headers = {
            'Authorization': f'Bearer {token}'
        }

        # create user
        data = USER_DATA["register"]
        data['password'] = 'John6b4pt15t'

        # pass in role_id
        data['role_id'] = self.role_id

        create_response = self.client.post(BASE_URL + "users/", data, headers=headers, format='multipart')
        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)

        # get a user
        url = BASE_URL + f"users/"
        response = self.client.get(url, headers=headers)

        user = response.data['results'][0]

        url = BASE_URL + f"users/{user['id']}/"
        updated_data = USER_DATA["update"]
        updated_data['role_id'] = self.role_id

        response = self.client.put(url, updated_data, headers=headers, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotEqual(response.data["first_name"], user["first_name"])
   

    def test_set_user_login(self):
        # log in as super admin
        token = self.get_auth_token(
            email=self.superadmin.email,
            password='superAdminUser'
        )

        headers = {
            'Authorization': f'Bearer {token}'
        }

        # create user
        data = USER_DATA["register"]
        data['password'] = 'John6b4pt15t'

        # pass in role_id
        data['role_id'] = self.role_id

        create_response = self.client.post(BASE_URL + "users/", data, headers=headers,format='multipart')
        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)

        # get a user
        url = BASE_URL + f"users/"
        response = self.client.get(url, headers=headers)

        user_obj = response.data['results'][0]

        user = User.objects.get(pk=user_obj['id'])

        # password reset info
        user_password_reset = USER_PASSWORD_DATA['set_password']
        user_password_reset['uidb64'] = urlsafe_base64_encode(force_bytes(user.id))
        user_password_reset['token'] = default_token_generator.make_token(user)

        url = BASE_URL + f"accounts/set-password/"
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

        # create user
        data = USER_DATA["register"]
        data['password'] = 'SecurePassword123!'

        # pass in role_id
        data['role_id'] = self.role_id

        create_response = self.client.post(BASE_URL + "users/", data, headers=headers, format='multipart')
        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)

        # get a user
        url = BASE_URL + f"users/"
        response = self.client.get(url, headers=headers)
        user_obj = response.data['results'][0]
    
        user = User.objects.get(pk=user_obj['id'])

        # activate user
        url = BASE_URL + f"users/{user.id}/activate/"
        response = self.client.get(url, headers=headers, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # password reset info
        user_password_reset = USER_PASSWORD_DATA['set_password']
        user_password_reset['uidb64'] = urlsafe_base64_encode(force_bytes(user.id))
        user_password_reset['token'] = default_token_generator.make_token(user)

        url = BASE_URL + f"accounts/set-password/"
        response = self.client.post(url, user_password_reset, format='json')

        url = BASE_URL + "token/"
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

        # create user
        data = USER_DATA["register"]
        data['password'] = 'John6b4pt15t'

        # pass in role_id
        data['role_id'] = self.role_id
  
        create_response = self.client.post(BASE_URL + "users/", data, headers=headers, format='multipart')
        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)
        
        # get a user
        url = BASE_URL + f"users/"
        response = self.client.get(url, headers=headers)

        user = response.data['results'][0]

        # delete
        url = BASE_URL + f"users/{user['id']}/"
        response = self.client.delete(url, headers=headers)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # # confirm deletion
        get_response = self.client.get(url, headers=headers)
        self.assertEqual(get_response.status_code, status.HTTP_404_NOT_FOUND)


class RolePermissionAPITestCase(APITestCase):

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
        role_permission_create = ROLE_PERMISSION_DATA["create"]
        role_permission_update = ROLE_PERMISSION_DATA["update"]
        role_permission_create["role_id"] = self.role.id
        role_permission_create["content_type_id"] = self.content_type.id

        role_permission_update["role_id"] = self.role.id
        role_permission_update["content_type_id"] = self.content_type.id

        self.list_url = BASE_URL + "permissions/"

    def get_auth_token(self, email=None, password=None):
        # get access and refresh token
        url = BASE_URL + 'token/'
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

    def test_create_role_permission(self):
        token = self.get_auth_token(
            email=self.superadmin.email,
            password='superAdminUser'
        )

        headers = {
            'Authorization': f'Bearer {token}'
        }

        data = ROLE_PERMISSION_DATA["create"]
        data['content_type_ids'] = [self.content_type.id]

        response = self.client.post(
            self.list_url,
            data,
            headers=headers,
            format="json"
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # validate read-only fields present
        self.assertIn("role", response.data)
        self.assertIn("content_type", response.data)

        # validate flag values
        self.assertTrue(response.data["can_create"])
        self.assertTrue(response.data["can_read"])

    def test_get_role_permission(self):
        token = self.get_auth_token(
            email=self.superadmin.email,
            password='superAdminUser'
        )

        headers = {
            'Authorization': f'Bearer {token}'
        }

        # create first
        data = ROLE_PERMISSION_DATA["create"]
        data['content_type_ids'] = [self.content_type.id]
        create_response = self.client.post(
            self.list_url,
            data,
            headers=headers,
            format="json"
        )
        permission_id = create_response.data["id"]

        url = BASE_URL + f"permissions/{permission_id}/"
        response = self.client.get(url, headers=headers)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["role"], str(self.role))
        self.assertEqual(response.data["content_type"]["id"], self.content_type.id)

    def test_update_role_permission(self):
        token = self.get_auth_token(
            email=self.superadmin.email,
            password='superAdminUser'
        )

        headers = {
            'Authorization': f'Bearer {token}'
        }

        # create first
        create_response = self.client.post(
            self.list_url,
            ROLE_PERMISSION_DATA["create"],
            headers=headers,
            format="json"
        )
        permission_id = create_response.data["id"]

        url = BASE_URL + f"permissions/{permission_id}/"
        response = self.client.put(
            url,
            ROLE_PERMISSION_DATA["update"],
            headers=headers,
            format="json"
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["can_update"])
        self.assertTrue(response.data["can_delete"])
        self.assertTrue(response.data["can_manage"])
        self.assertTrue(response.data["can_dispatch_driver"])

    def test_delete_role_permission(self):
        token = self.get_auth_token(
            email=self.superadmin.email,
            password='superAdminUser'
        )

        headers = {
            'Authorization': f'Bearer {token}'
        }

        # create first
        create_response = self.client.post(
            self.list_url,
            ROLE_PERMISSION_DATA["create"],
            headers=headers,
            format="json"
        )
        permission_id = create_response.data["id"]

        url = BASE_URL + f"permissions/{permission_id}/"
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

        # create first instance
        self.client.post(
            self.list_url,
            ROLE_PERMISSION_DATA["create"],
            headers=headers,
            format="json"
        )

        # attempt to create duplicate role + content_type pair
        response = self.client.post(
            self.list_url,
            ROLE_PERMISSION_DATA["create"],
            headers=headers,
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Double entry for permission", response.data)

    def test_get_content_types(self):
        url = BASE_URL + 'content-types/'
        token = self.get_auth_token(
            email=self.superadmin.email,
            password='superAdminUser'
        )

        headers = {
            'Authorization': f'Bearer {token}'
        }

        # create first instance
        resp = self.client.get(url, headers=headers)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data), 3)


class APIThrottlingTest(APITestCase):
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

    def get_auth_token(self, email=None, password=None):
        # get access and refresh token
        url = BASE_URL + 'token/'
        data = {
            'email': email,
            'password': password
        }

    def test_anon_throttling(self):
        '''Test Anonymouse throttling at 20/min'''
        url = BASE_URL + 'accounts/password-reset/'

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
    

class AuthenticationTestCase(APITestCase):
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
        url = BASE_URL + 'token/'
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
        url = BASE_URL + 'token/'
        data = {
            'email': 'wrong@mzansilogistic.com',
            'password': self.password
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_03_login_invalid_password(self):
        """Test login with invalid password"""
        url = BASE_URL + 'token/'
        data = {
            'email': self.user_data['email'],
            'password': 'WrongPassword123!'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_04_login_missing_fields(self):
        """Test login with missing fields"""
        url = BASE_URL + 'token/'
        
        # Missing password
        response = self.client.post(url, {'email': self.user_data['email']}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Missing email
        response = self.client.post(url, {'password': self.password}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_05_token_refresh_success(self):
        """Test successful token refresh"""
        # First, login to get tokens
        login_url = BASE_URL + 'token/'
        login_data = {
            'email': self.user_data['email'],
            'password': self.password
        }
        login_response = self.client.post(login_url, login_data, format='json')
        refresh_token = login_response.data['refresh']
        
        # Now refresh the token
        refresh_url = BASE_URL + 'token/refresh/'
        refresh_data = {'refresh': refresh_token}
        response = self.client.post(refresh_url, refresh_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIsNotNone(response.data['access'])
        self.assertIsNotNone(response.data['refresh'])
    
    def test_06_token_refresh_invalid(self):
        """Test token refresh with invalid refresh token"""
        refresh_url = BASE_URL + 'token/refresh/'
        refresh_data = {'refresh': 'invalid_refresh_token'}
        response = self.client.post(refresh_url, refresh_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_07_protected_endpoint_without_token(self):
        """Test accessing protected endpoint without token"""
        url = BASE_URL + 'users/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_08_protected_endpoint_with_valid_token(self):
        """Test accessing protected endpoint with valid token"""
        # Login to get token
        login_url = BASE_URL + 'token/'
        login_data = {
            'email': self.user_data['email'],
            'password': self.password
        }
        login_response = self.client.post(login_url, login_data, format='json')
        access_token = login_response.data['access']
        
        # Access protected endpoint
        url = BASE_URL + 'users/'
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_09_password_reset_request(self):
        """Test password reset request"""
        url = BASE_URL + 'accounts/password-reset/'
        data = {
            'account': self.user_data['email'],
            'email': self.user_data['email']
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('detail', response.data)
        
        # Check that email was sent (UNCOMMENT after setting up Email Service)
        # self.assertEqual(len(mail.outbox), 1)
        # self.assertIn('MzansiLogistics Password', mail.outbox[0].subject)

    def test_10_password_reset_invalid_email(self):
        """Test password reset with non-existent email"""
        url = BASE_URL + 'accounts/password-reset/'
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
        
        url = BASE_URL + 'accounts/set-password/'
        data = {
            'uidb64': uid,
            'token': token,
            'new_password': 'NewPassword123!'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify new password works
        login_url = BASE_URL + 'token/'
        login_data = {
            'email': self.user_data['email'],
            'password': 'NewPassword123!'
        }
        login_response = self.client.post(login_url, login_data, format='json')
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)

    def test_12_set_password_invalid_token(self):
        """Test setting password with invalid token"""
        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        
        url = BASE_URL + 'accounts/set-password/'
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
        
        url = BASE_URL + 'accounts/set-password/'
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
        
        url = BASE_URL + 'token/'
        data = {
            'email': self.user_data['email'],
            'password': self.password
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_15_concurrent_logins(self):
        """Test multiple concurrent logins (tokens)"""
        url = BASE_URL + 'token/'
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
        protected_url = BASE_URL + 'users/'
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token1}')
        response = self.client.get(protected_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token2}')
        response = self.client.get(protected_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class RoleBasedAccessTestCase(APITestCase):
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

    def get_token(self, user_email, password):
        """Helper to get access token"""
        url = BASE_URL + 'token/'
        data = {'email': user_email, 'password': password}
        response = self.client.post(url, data, format='json')
        return response.data['access']

    def test_admin_access(self):
        """Test admin can access admin endpoints"""
        token = self.get_token('admin@mzansilogistic.org', 'AdminPass123!')
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.get(BASE_URL + 'roles/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_regular_user_access(self):
        """Test regular user can access their own data"""
        token = self.get_token('user@mzansilogistic.org', 'UserPass123!')
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.get(BASE_URL + 'users/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)