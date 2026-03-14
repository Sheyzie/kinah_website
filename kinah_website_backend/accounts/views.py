from django.contrib.auth import get_user_model
from django.db.models import Q, Count
from django.contrib.contenttypes.models import ContentType
from rest_framework import viewsets, generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.decorators import action, api_view, permission_classes, throttle_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample
from django.db.models.functions import ExtractMonth
from datetime import date

from .permissions import (
    IsAdminUser, RoleBasedPermission,
    IsStaffUser, CanCreateAccount,
    CanManageResource, CanDispatchDriver
)
from .models import Role, RolePermission
from .serializers import (
    UserSerializer,
    RoleSerializer,
    RolePermissionSerializer,
    SetPasswordSerializer
)
from .utils import build_password_reset_link, get_monthly_data
from .tasks import send_password_reset_link_task

User = get_user_model()


class BaseModelViewSet(viewsets.ModelViewSet):
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

    def handle_exception(self, exc):
        """Handle exceptions consistently across all ViewSets"""
        if isinstance(exc, (KeyError, ValueError)):
            return self.failure(
                message={"detail": str(exc)},
            )
        return super().handle_exception(exc)
    
        
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        model_name = serializer.Meta.model.__name__ # get model name

        if serializer.is_valid(raise_exception=True):
            self.perform_create(serializer)
            return self.success(
                data=serializer.data,
                message=f"{model_name} created successfully",
                code=201
            )

        return self.failure(
            errors=serializer.errors,
            message=f"{model_name}  creation failed",
            code=400
        )
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        model_name = queryset.model.__name__ # get model name
        data = {
            'count': len(serializer.data),
            'data': serializer.data
        }

        return self.success(
            data=data,
            message=f"{model_name}  retrieved successfully",
        )
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        model_name = instance.__class__.__name__ # get model name

        return self.success(
            data=serializer.data,
            message=f"{model_name} retrieved successfully"
        )
    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=False)
        model_name = instance.__class__.__name__ # get model name

        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return self.success(
                data=serializer.data,
                message=f"{model_name} updated successfully"
            )

        return self.failure(
            errors=serializer.errors,
            message=f"{model_name} update failed"
        )
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        model_name = instance.__class__.__name__
        instance.delete()
        return self.success(
            message=f"{model_name} deleted successfully",
            code=204
        )


class UserViewSet(BaseModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    parser_classes = [MultiPartParser, FormParser]
    filter_backends = [SearchFilter, OrderingFilter]
    permission_classes = [RoleBasedPermission]
    throttle_classes = [UserRateThrottle]
    search_fields = ['first_name', 'last_name', 'email', 'phone']
    ordering_fields = ['first_name', 'last_name', 'email', 'created_at', 'updated_at']
    ordering = ['-created_at']

    # def get_permissions(self):
    #     if self.action == 'activate':
    #         return [IsAdminUser()]
    #     return super().get_permissions()

    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.query_params.get('search', '').strip()

        if search_query:
            # Sanitize search query
            sanitized_query = ''.join(char for char in search_query if char.isalnum() or char in [' ', '@', '.', '-', '_', '+'])

            if sanitized_query:
                search_conditions = (
                    Q(first_name__icontains=sanitized_query) |
                    Q(last_name__icontains=sanitized_query) |
                    Q(email__icontains=sanitized_query) |
                    Q(phone__icontains=sanitized_query) |
                    Q(role__role_name__icontains=sanitized_query)
                )
                queryset = queryset.filter(search_conditions)

        # Additional filtering
        filters = {
            'role_id': lambda x: queryset.filter(role_id=int(x)),
            'is_active': lambda x: queryset.filter(is_active=x.lower() == 'true')
        }

        for param, filter_func in filters.items():
            value = self.request.query_params.get(param)
            if value and (param != 'is_active' or value in ['true', 'false']):
                queryset = filter_func(value)

        return queryset.select_related('role')

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated]) # , permission_classes=[IsAuthenticated]
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return self.success(
            message='User retrieved succesfully',
            data=serializer.data,
            code=200
        )
    
    @action(detail=True, methods=['get'], permission_classes=[IsStaffUser]) # , permission_classes=[IsAuthenticated]
    def activate(self, request, pk=None):
        user = self.get_object()
        user.is_active = True
        user.save()
        return self.success(
            message='User activated successfully',
            code=200
        )
    
    @action(detail=True, methods=['get'], permission_classes=[IsStaffUser]) # , permission_classes=[IsAuthenticated]
    def deactivate(self, request, pk=None):
        user = self.get_object()
        user.is_active = False
        user.save()
        return self.success(
            message='User deactivated successfully',
            code=200
        )

    @action(detail=True, methods=['post'], permission_classes=[AllowAny])
    def set_password(self, request, pk=None):
        user = self.get_object()
        serializer = SetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user.set_password(serializer.validated_data['password'])
        user.save()
        return self.success(
            message='Password has been set successfully.',
            code=200
        )


class RoleViewSet(BaseModelViewSet):
    serializer_class = RoleSerializer
    queryset = Role.objects.all()
    filter_backends = [SearchFilter, OrderingFilter]
    permission_classes = [RoleBasedPermission]
    throttle_classes = [UserRateThrottle]
    search_fields = ['role_name', 'color']
    ordering_fields = ['id', 'role_name', 'is_admin', 'is_default']
    ordering = ['role_name']

    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.query_params.get('search', '').strip()

        if search_query:
            queryset = queryset.filter(
                Q(role_name__icontains=search_query) |
                Q(color__icontains=search_query)
            )

        return queryset


class RolePermissionViewSet(BaseModelViewSet):
    serializer_class = RolePermissionSerializer
    queryset = RolePermission.objects.all()
    permission_classes = [RoleBasedPermission]
    throttle_classes = [UserRateThrottle]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['role__role_name', 'content_type__model']
    ordering_fields = ['role__role_name', 'content_type__model']
    ordering = ['role__role_name']

    def get_queryset(self):
        queryset = super().get_queryset().select_related('role', 'content_type')

        search_query = self.request.query_params.get('search', '').strip()

        if search_query:
            queryset = queryset.filter(
                Q(role__role_name__icontains=search_query) |
                Q(content_type__model__icontains=search_query)
            )

        return queryset

    # def list(self, request, *args, **kwargs):
    #     response = super().list(request, *args, **kwargs)
    #     # Ensure consistent response format
    #     if isinstance(response.data, list):
    #         response.data = {
    #             'count': len(response.data),
    #             'results': response.data
    #         }
    #     return super().list()


# Authentication Views
class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    throttle_classes = [UserRateThrottle]

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

    @extend_schema(
        request={"refresh": "string"},
        responses={
            200: OpenApiResponse(description="Successfully logged out"),
            400: OpenApiResponse(description="Invalid or missing token"),
        },
    )
    def post(self, request):
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return self.failure(
                message="Refresh token is required",
                code=status.HTTP_400_BAD_REQUEST
            )

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            return self.success(
                message="Successfully logged out",
                code=status.HTTP_200_OK
            )
        except TokenError:
            return self.failure(
                message="Token not valid",
                code=status.HTTP_400_BAD_REQUEST
            )
        except Exception:
            return self.failure(
                message="Log out failed",
                code=status.HTTP_400_BAD_REQUEST
            )


class LogoutAllView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    throttle_classes = [UserRateThrottle]

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

    @extend_schema(
        responses={200: OpenApiResponse(description="Logged out on all devices")}
    )
    def post(self, request):
        tokens = OutstandingToken.objects.filter(user=request.user)
        for token in tokens:
            try:
                RefreshToken(token.token).blacklist()
            except Exception:
                pass
        return self.success(
            message="Successfully logged out from all devices"
        )


class SetPasswordView(generics.GenericAPIView):
    serializer_class = SetPasswordSerializer
    permission_classes = [AllowAny]
    throttle_classes = [AnonRateThrottle]

    def success(self, data=None, message="Success", code=status.HTTP_200_OK):
        return Response({
            "status": "success",
            "message": message,
            "data": data
        }, status=code)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return self.success(
            message="Password has been set successfully."
        )


# API Views
@extend_schema(
    responses={
        200: OpenApiResponse(
            description="List of content types",
        )
    }
)
@api_view(['GET'])
@throttle_classes([UserRateThrottle])
@permission_classes([IsAdminUser])
def get_content_types(request):
    """Get all content types for objects dropdown"""
    
    Model_Map = {
        'accounts': {'role', 'rolepermission', 'user'},
        'finance': {
            'address', 'order', 'coupon', 'payment'
        },
        'logistics': {'vehicle', 'dispatch'},
        'products': {'productscategory', 'productstype', 'product', 'review'},
    }

    try:
        content_types = ContentType.objects.all().order_by('app_label', 'model')
        data = [
            {
                'id': ct.id,
                'app_label': ct.app_label,
                'model': ct.model,
                'name': f"{ct.app_label}.{ct.model}"
            }
            for ct in content_types
            if ct.model in Model_Map.get(ct.app_label, {})
        ]
        return Response({
            'status': "success",
            "message": "Contentypes retrieved successfully",
            "data": {
                "count": len(data),
                "data": data
            }
        })
    except Exception as e:
        return Response({
                "status": "failure",
                "message": 'Failed to fetch content types',
                "errors": {str(e)}
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@extend_schema(
    responses={
        200: OpenApiResponse(description="List of permission options")
    }
)
@api_view(['GET'])
@throttle_classes([UserRateThrottle])
@permission_classes([RoleBasedPermission])
def get_permission_options(request):
    """Get available permission options"""
    permission_options = [
        {'id': 'can_create', 'name': 'Can Create'},
        {'id': 'can_read', 'name': 'Can Read'},
        {'id': 'can_update', 'name': 'Can Update'},
        {'id': 'can_delete', 'name': 'Can Delete'},
        {'id': 'can_manage', 'name': 'Can Manage'},
        {'id': 'can_create_account', 'name': 'Can Create Account'},
        {'id': 'can_dispatch_driver', 'name': 'Can Dispatch Driver'},
    ]
    return Response({
        'status': "success",
        "message": "Contentypes retrived success fully",
        "data": {
            "count": len(permission_options),
            "data": permission_options
        }
    }, status=status.HTTP_200_OK)


@extend_schema(
    responses={
        200: OpenApiResponse(description="User counts per role")
    }
)
@api_view(['GET'])
@throttle_classes([UserRateThrottle])
@permission_classes([IsAdminUser])
def role_user_counts(request):
    """Returns user counts for all roles."""
    try:
        roles_with_counts = Role.objects.annotate(
            user_count=Count('users', distinct=True)
        ).values('id', 'role_name', 'user_count')

        counts_dict = {role['id']: role['user_count'] for role in roles_with_counts}
        return Response({
            'status': "success",
            "message": "Contentypes retrived success fully",
            "data": counts_dict
        })
    except Exception as e:
        return Response({
            "status": "failure",
            "message": 'Failed to get role user counts',
            "errors": {str(e)}
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@extend_schema(
    request={"role_ids": ["integer"]},
    responses={
        200: OpenApiResponse(description="User counts for specific roles")
    }
)
@api_view(['POST'])
@throttle_classes([UserRateThrottle])
@permission_classes([IsAdminUser])
def specific_role_user_counts(request):
    """Returns user counts for specific role IDs."""
    try:
        role_ids = request.data.get('role_ids', [])
        if not role_ids:
            return Response({})

        roles_with_counts = Role.objects.filter(id__in=role_ids).annotate(
            user_count=Count('users', distinct=True)
        ).values('id', 'user_count')

        counts_dict = {role['id']: role['user_count'] for role in roles_with_counts}
        return Response({
            'status': "success",
            "message": "Content types retrived successfully",
            "data": counts_dict
        })
    except Exception as e:
        return Response({
            "status": "failure",
            "message": 'Failed to get specific role user counts',
            "errors": {str(e)}
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@extend_schema(
    request={"type": "object", "properties": {"account": {"type": "string"}, "email": {"type": "string"}}},
    responses={200: OpenApiResponse(description="Password reset processed")}
)
@api_view(['POST'])
@throttle_classes([AnonRateThrottle])
@permission_classes([AllowAny])
def password_reset_request(request):
    """Handle password reset requests"""
    account = request.data.get('account')
    email = request.data.get('email')

    if not email:
        return Response({
            "status": "failure",
            "message": 'Account and email are required',
        }, status=status.HTTP_400_BAD_REQUEST)

    user = get_user_by_email(email)

    if user:
        reset_link = build_password_reset_link(user=user, request=request)
        send_password_reset_link_task.delay(user_id=user.id, reset_link=reset_link, password=None)

    return Response({
            "status": "success",
            "message": f'A reset link has been sent to {email}',
        }, status=status.HTTP_200_OK)


# Utility functions
def get_user_by_email(email):
    """Get user by email or return None"""
    try:
        return User.objects.get(email=email)
    except User.DoesNotExist:
        return None


@api_view(['GET'])
@throttle_classes([UserRateThrottle])
@permission_classes([RoleBasedPermission])
def dashboard(request):
    # clients_count = Contact.objects.count()
    # revenue_total = sum(inv.total_amount for inv in Invoice.objects.all())
    # total_payable = sum(bill.amount_paid for bill in Bill.objects.filter(payment_status='pending'))
    # due_invoices = Invoice.objects.filter(due_date__lte=date.today())

    # due_invoices_data = []
    # for inv in due_invoices:
    #     if inv.balance > 0:
    #         due_invoices_data.append({
    #             'id': inv.id,
    #             'invoice_number': inv.invoice_number,
    #             'client': f'{inv.client.first_name} {inv.client.last_name}',
    #             'amount': inv.balance,
    #             'due_date': inv.due_date
    #         })

    # current_year = date.today().year
    # sales_by_month = get_monthly_data(current_year)

    # return Response({
    #     'clients_count': clients_count,
    #     'revenue_total': revenue_total,
    #     'total_payable': total_payable,
    #     'due_invoices': due_invoices_data,
    #     'sales_by_month': sales_by_month
    # })

    pass