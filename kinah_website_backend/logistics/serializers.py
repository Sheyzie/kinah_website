from rest_framework import serializers
from django.db import transaction
from finance.models import Address
from accounts.models import Role
from accounts.permissions import DefaultPermission
from .models import Vehicle, Dispatch
from typing import Any


from django.contrib.auth import get_user_model

import logging
logger = logging.getLogger(__name__)


User = get_user_model()


class VehicleSerializer(serializers.ModelSerializer):
    """
    Serializer for Vehicle model
    """
    
    class Meta:
        model = Vehicle
        fields = [
            "id", "vehicle_type", "vehicle_brand", "plate_number", 
            "plate_state", "plate_country", "color", "created_at",
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class DispatchListDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for Dispatch model for list and view
    """

    driver = serializers.SerializerMethodField(read_only=True)
    vehicle = serializers.SerializerMethodField(read_only=True)
    company_address = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Dispatch
        fields = [
            'id', 'driver', 'company_name', 'company_address', 'cost_per_km', 'vehicle',
            'is_active','status', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'is_active','status', 'created_at', 'updated_at']

    def get_driver(self, obj):
        if not obj.driver:
            return None
    
        return {
            'id': obj.driver.id,
            'name': obj.driver.full_name,
            'email': obj.driver.email,
        }
    
    def get_vehicle(self, obj):
        if not obj.vehicle:
            return None
        return {
            'id': obj.vehicle.id,
            'vehicle_type': obj.vehicle.vehicle_type,
            'plate': obj.vehicle.plate_number,
        }
    
    def get_company_address(self, obj):
        if not obj.company_address:
            return None
        return {
            'full_address': obj.company_address.full_address,
            'street_address': obj.company_address.street_address,
            'apartment_address': obj.company_address.apartment_address,
            'city': obj.company_address.city,
            'state': obj.company_address.state,
            'postal_code': obj.company_address.postal_code,
            'country': obj.company_address.country,
        }
    

class DispatchCreateSerializer(serializers.ModelSerializer):
    """
    Serializer to Create Dispatch model
    """
    driver = serializers.DictField(write_only=True)
    company_address = serializers.DictField(write_only=True)
    vehicle = serializers.DictField(write_only=True)
    
    class Meta:
        model = Dispatch
        fields = [
            'id', 'driver', 'company_name', 'company_address', 'cost_per_km', 'vehicle',
            'is_active', 'status', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'is_active', 'status', 'created_at', 'updated_at']

    def validate(self, data):
        """
        Validate address data
        """
        logger.info('Validating dispatch data')
        DRIVER_ALLOWED_KEYS = {'first_name', 'last_name', 'email', 'phone', 'password'}

        ADDRESS_ALLOWED_KEYS = [
            'street_address', 
            'apartment_address', 'city', 'state', 'postal_code',
            'country', 'latitude', 'longitude'
        ]

        VEHICLE_ALLOWED_KEYS = [
            'vehicle_type', 'vehicle_brand', 'plate_number', 
            'plate_state', 'plate_country', 'color'
        ]

        driver_data = data.get('driver', None)
        company_address_data = data.get('company_address', None)
        vehicle_data = data.get('vehicle', None)
        company_name = data.get('company_name', None)

        if driver_data is None:
            raise serializers.ValidationError(
                {"driver": "Driver is required."}
            )
        
        if company_address_data is None:
            raise serializers.ValidationError(
                {"company_address": "Company address is required."}
            )
        
        if vehicle_data is None:
            raise serializers.ValidationError(
                {"vehicle": "Vehicle is required."}
            )
        
        if company_name is None:
            raise serializers.ValidationError(
                {"company_name": "Company name is required."}
            )

        if not isinstance(driver_data, dict):
            raise serializers.ValidationError(
                {"driver": "Driver data should be a dictionary."}
            )
        
        if not isinstance(company_address_data, dict):
            raise serializers.ValidationError(
                {"company_address": "Company address data should be a dictionary."}
            )
        
        if not isinstance(vehicle_data, dict):
            raise serializers.ValidationError(
                {"vehicle": "vehicle data should be a dictionary."}
            )
        
        if not isinstance(company_name, str):
            raise serializers.ValidationError(
                {"company_name": "Company name should be a string."}
            )
        
        driver: dict[str, Any] = driver_data
        company_address: dict[str, Any] = company_address_data
        vehicle: dict[str, Any] = vehicle_data

        missing = DRIVER_ALLOWED_KEYS - driver.keys()

        if missing:
            raise serializers.ValidationError(
                {"driver": f"Missing fields: {missing}"}
            )
        
        missing = ADDRESS_ALLOWED_KEYS - company_address.keys()

        if missing:
            raise serializers.ValidationError(
                {"company_address": f"Missing fields: {missing}"}
            )
        
        missing = VEHICLE_ALLOWED_KEYS - vehicle.keys()

        if missing:
            raise serializers.ValidationError(
                {"vehicle": f"Missing fields: {missing}"}
            )
        
        return data

    @transaction.atomic
    def create(self, validated_data):
        logger.info('Creating dispatch')

        driver_data = validated_data.pop('driver', None)
        company_address = validated_data.pop('company_address', None)
        vehicle_data = validated_data.pop('vehicle', None)
        company_name = validated_data.get('company_name', None)

        if not driver_data or not company_address or not vehicle_data:
            raise serializers.ValidationError('Invalid data')
        
        driver = self.create_driver(driver_data)
        address = self.create_company_address(driver, company_address)
        vehicle = self.create_vehicle(vehicle_data)

        dispatch = Dispatch.objects.create(
            driver=driver,
            vehicle=vehicle,
            company_name=company_name,
            company_address=address,
            is_active=True,
            status='available'
        )

        return dispatch

    def create_driver(self, driver_dict: dict[str, Any]):
        ALLOWED_KEYS = {'first_name', 'last_name', 'email', 'phone'}
        # TODO: Validate photo to not contain malicious content

        password = driver_dict.get('password', None)
        if not password:
            raise serializers.ValidationError({
                "password": "Password is required"
            })
        
        driver_data = {}
        for key, value in driver_dict.items():
            if key in ALLOWED_KEYS and value:
                driver_data[key] = value

        if User.objects.filter(email=driver_data.get("email")).exists():
            raise serializers.ValidationError({
                "driver": "User with this email already exists"
            })
        
        role, created = Role.objects.get_or_create(role_name='dispatcher', defaults={
            'color': "#b700ff",
            'is_admin': False,
            'is_default': False,
            'is_active': True,
            'is_editable': False
        })

        if created:
            perms = DefaultPermission(role)
            perms.set_dispatcher_default_perms()

        driver = User.objects.create_user(role=role, **driver_data)
        driver.set_password(password)
        driver.is_active = True
        driver.save()

        return driver

    def create_company_address(self, driver, company_address: dict[str, Any]):
        if not isinstance(driver, User):
            raise serializers.ValidationError('Driver in address data is not a User instance')
        
        ALLOWED_KEYS = [
            'full_name', 'street_address', 
            'apartment_address', 'city', 'state', 'postal_code',
            'country'
        ]

        address_data = {}
        for key, value in company_address.items():
            if key in ALLOWED_KEYS and value:
                address_data[key] = value
            
        address_data['address_type'] = 'office'
        address = Address.objects.create(user=driver, **address_data)

        return address
        
    def create_vehicle(self, vehicle_dict: dict[str, Any]):
        ALLOWED_KEYS = [
            'vehicle_type', 'vehicle_brand', 'plate_number', 
            'plate_state', 'plate_country', 'color'
        ]

        vehicle_data = {}
        for key, value in vehicle_dict.items():
            if key in ALLOWED_KEYS and value:
                vehicle_data[key] = value
        
        vehicle = Vehicle.objects.create(**vehicle_data)
        return vehicle


class DispatchUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating dispatch status
    """
    status = serializers.ChoiceField(choices=Dispatch.STATUS_CHOICE)
    
    def update_status(self, instance):
        """
        Update dispatch status and create history
        """
        old_status = instance.status
        new_status = self.validated_data['status']
        instance.status = new_status
        instance.save()
        
        return instance
  