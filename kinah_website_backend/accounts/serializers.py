from rest_framework import serializers
from django.db import transaction
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType

from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str

from .models import Role, RolePermission
from .utils import build_password_reset_link
from .tasks import send_password_reset_link_task, send_welcome_email_task, send_email_verification_task


User = get_user_model()


class RoleSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(read_only=True)
    class Meta:
        model = Role
        fields = ['id', 'role_name', 'color', 'is_admin', 'is_editable', 'is_default', 'is_active']

    def update(self, instance, validated_data):
        user = self.context['request'].user
        if not instance.is_editable:
            if not user.is_superuser or not (hasattr(user, 'role') and  user.role.is_admin):
                return serializers.ValidationError('Only an admin user can update this role')
        return super().update(instance, validated_data)


class ContentTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContentType
        fields = ['id', 'app_label', 'model']


class RolePermissionSerializer(serializers.ModelSerializer):
    role_id = serializers.PrimaryKeyRelatedField(
        queryset=Role.objects.all(),
        source='role',
        write_only=True
    )
    # content_type_id = serializers.PrimaryKeyRelatedField(
    #     queryset=ContentType.objects.all(),
    #     source='content_type',
    #     write_only=True,
    # )
    content_type_ids = serializers.ListField(
        child=serializers.PrimaryKeyRelatedField(
            queryset=ContentType.objects.all()
        ),
        write_only=True
    )
    role = serializers.StringRelatedField(read_only=True)  # or use nested RoleSerializer
    content_type = ContentTypeSerializer(read_only=True)

    class Meta:
        model = RolePermission
        fields = [
            'id', 'role', 'role_id',
            'content_type', 'content_type_ids',
            'can_create', 'can_read', 'can_update', 'can_delete',
            'can_manage', 'can_create_account', 'can_dispatch_driver'
        ]

    def create(self, validated_data):
        content_types = validated_data.pop('content_type_ids', None)

        if content_types is None or len(content_types) == 0:
            raise serializers.ValidationError('Content Type is Required')

        permissions = []

        with transaction.atomic():
            for content_type in content_types:
                try:
                    permission = RolePermission.objects.create(
                        content_type=content_type,
                        **validated_data
                    )
                    permissions.append(permission)
                except Exception as e:
                    raise serializers.ValidationError('Double entry for permission')

        # Return the first instance (DRF expects one object)
        return permissions[0]

    def update(self, instance, validated_data):
        content_types = validated_data.pop('content_type_ids', None)
        role = instance.role

        # permission flags
        permission_fields = {
            k: v for k, v in validated_data.items()
            if k.startswith('can_')
        }

        updated_permissions = []

        with transaction.atomic():
            if content_types is not None:
                existing_permissions = RolePermission.objects.filter(
                    role=role,
                    content_type__in=content_types
                )

                # Update existing ones
                for perm in existing_permissions:
                    for field, value in permission_fields.items():
                        setattr(perm, field, value)
                    perm.save()
                    updated_permissions.append(perm)

                existing_ct_ids = set(
                    existing_permissions.values_list('content_type', flat=True)
                )

                # Create missing ones
                for content_type in content_types:
                    if content_type.id not in existing_ct_ids:
                        perm = RolePermission.objects.create(
                            role=role,
                            content_type=content_type,
                            **permission_fields
                        )
                        updated_permissions.append(perm)

        # DRF expects a single instance — return one
        return updated_permissions[0] if updated_permissions else instance


class UserSerializer(serializers.ModelSerializer):
    role_id = serializers.PrimaryKeyRelatedField(
        queryset=Role.objects.all(),
        source='role',
        write_only=True,
        required=False,
        allow_null=True
    )
    role = serializers.SerializerMethodField()

    password = serializers.CharField(write_only=True, required=False, allow_null=True)

    class Meta:
        model = User
        fields = [
            'id', 'first_name', 'last_name', 'email', 'phone',
            'role', 'role_id', 'photo',
            'is_active', 'is_staff', 'created_at', 'updated_at', 'password'
        ]

    def get_role(self, obj):
        return {
            "role_id": obj.role.id,
            "role_name": obj.role.role_name,
            "color": obj.role.color
        }
        

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        role = validated_data.pop('role', None)
        is_staff = validated_data.pop('is_staff', None)
        is_superuser = validated_data.pop('is_superuser', None)

        if password is None:
            raise  serializers.ValidationError('Password is required')

        try:
            if role is None:
                role = Role.objects.get(is_default=True)

            user = User.objects.create_user(role=role, **validated_data)
            user.set_password(password)
            user.save()

            # Send password reset link
            reset_link = build_password_reset_link(user=user, request=self.context['request'])
            send_welcome_email_task.delay(user_id=user.id)
            send_email_verification_task(user_id=user.id, reset_link=reset_link)

            # send_password_reset_link_task.delay(user_id=user.id, reset_link=reset_link, password=password)

            return user

        except Role.DoesNotExist:
            raise  serializers.ValidationError('Role ID is required')

    def update(self, instance, validated_data):
        validated_data.pop('password', None)
        is_staff = validated_data.pop('is_staff', None)
        is_superuser = validated_data.pop('is_superuser', None)
        return super().update(instance, validated_data)


class SetPasswordSerializer(serializers.Serializer):
    uidb64 = serializers.CharField()
    token = serializers.CharField()
    new_password = serializers.CharField(write_only=True, min_length=8)

    def validate(self, attrs):
        uid = attrs.get('uidb64')
        token = attrs.get('token')
        try:
            uid = force_str(urlsafe_base64_decode(uid))
            self.user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            raise serializers.ValidationError("Invalid link.")

        # check if token is valid
        if not default_token_generator.check_token(self.user, token):
            raise serializers.ValidationError("Invalid or expired token.")
        return attrs

    def save(self):
        password = self.validated_data['new_password']
        self.user.set_password(password)
        self.user.save()
        return self.user

