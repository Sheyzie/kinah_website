from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.contrib.contenttypes.models import ContentType
from phonenumber_field.modelfields import PhoneNumberField
from django.db import models, transaction
import uuid
from django.utils import timezone 
from .permissions import DefaultPermission

class Role(models.Model):
    role_name = models.CharField(max_length=50, unique=True)
    color = models.CharField(max_length=20)
    is_admin = models.BooleanField(default=False)
    is_editable = models.BooleanField(default=True)
    is_default = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return self.role_name
    
    def save(self, *args, **kwargs):
        if self.is_default:
            Role.objects.filter(is_default=True).update(is_default=False)
        super().save(*args, **kwargs)


class UserManager(BaseUserManager):
    @transaction.atomic
    def create_user(
            self, 
            email: str, 
            first_name: str, 
            last_name: str, 
            phone: str, 
            password: str=None,
            role: Role=None,
            **extra_fields
        ):
 
        if not email:
            raise ValueError('The Email must be set')
        if not first_name:
            raise ValueError('The First Name must be set')
        if not last_name:
            raise ValueError('The Last Name must be set')
        if not phone:
            raise ValueError('The Phone must be set')
        
        if not role:
            role, created = Role.objects.get_or_create(role_name='buyer', defaults={
                'color': "#ee3b9d",
                'is_admin': False,
                'is_default': True,
                'is_active': True,
                'is_editable': False
            })

            if created:
                perms = DefaultPermission(role)
                perms.set_buyer_default_perms()
        
        email = self.normalize_email(email)
        user = self.model(
            email=email,
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            role=role,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        
        return user

    @transaction.atomic
    def create_superuser(
        self, 
            email: str, 
            first_name: str, 
            last_name: str, 
            phone: str, 
            password: str=None, 
            **extra_fields
        ):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        role, created = Role.objects.get_or_create(role_name='admin', defaults={
            'color': '#00ff00',
            'is_admin': True,
            'is_default': False,
            'is_active': True,
            'is_editable': False
        })

        if created:
            perms = DefaultPermission(role)
            perms.set_admin_default_perms()

        user = self.create_user(email, first_name, last_name, phone, password, role=role, **extra_fields)
        
        return user
    
    @transaction.atomic
    def create_staffuser(
        self, 
            email: str, 
            first_name: str, 
            last_name: str, 
            phone: str, 
            password: str=None, 
            **extra_fields
        ):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is True:
            raise ValueError('Staff user must have is_staff=False.')
        if extra_fields.get('is_superuser') is True:
            raise ValueError('Staff user must have is_superuser=False.')
        
        role, created = Role.objects.get_or_create(role_name='staff', defaults={
            'color': "#ffbb00",
            'is_admin': False,
            'is_default': False,
            'is_active': True,
            'is_editable': True
        })

        if created:
            perms = DefaultPermission(role)
            perms.set_staff_default_perms()

        user = self.create_user(email, first_name, last_name, phone, password, role=role, **extra_fields)
        
        return user


class RolePermission(models.Model):
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name='role_permissions', null=True, blank=True) 
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    can_create = models.BooleanField(default=False)
    can_read = models.BooleanField(default=False)
    can_update = models.BooleanField(default=False)
    can_delete = models.BooleanField(default=False)
    can_manage = models.BooleanField(default=False)
    can_create_account = models.BooleanField(default=False)
    can_dispatch_driver = models.BooleanField(default=False)

    class Meta:
        unique_together = ('role', 'content_type')

    def __str__(self):
        return f"{self.role.role_name} - {self.content_type.model}"
    
   
class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = None  # Remove the username field
    email = models.CharField(max_length=100, unique=True)
    phone = PhoneNumberField(unique=True)
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name='users', null=True, blank=True)
    photo = models.ImageField(upload_to='users/photos/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)  
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'phone']

    objects = UserManager()

    def __str__(self):
        return f'{self.first_name} {self.last_name}'

    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name}'

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'User'
        verbose_name_plural = 'Users'


class OTPRecord(models.Model):
    EVENT_CHOICES = (
        ('verify', 'Verify'),
        ('cancel', 'Cancel'),
    )

    otp = models.CharField(max_length=6, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    order = models.ForeignKey('finance.Order', on_delete=models.CASCADE, null=True, blank=True)
    event = models.CharField(max_length=20, choices=EVENT_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)