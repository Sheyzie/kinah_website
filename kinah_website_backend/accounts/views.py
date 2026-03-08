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
    CanCreateAccount, CanDispatchDriver,
    CanManageResource
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
    """Base ViewSet with common functionality"""

    def handle_exception(self, exc):
        """Handle exceptions consistently across all ViewSets"""
        if isinstance(exc, (KeyError, ValueError)):
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().handle_exception(exc)


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

        return queryset.select_related('role', 'department', 'station', 'employee')

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        self.perform_create(serializer)
        # Send password reset link
        # send_password_reset_link(user=serializer.instance, request=request)

        return Response(
            {"detail": "User created successfully. Email has been sent to set password."},
            status=status.HTTP_201_CREATED
        )

    @action(detail=False, methods=['get']) # , permission_classes=[IsAuthenticated]
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def set_password(self, request, pk=None):
        user = self.get_object()
        serializer = SetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user.set_password(serializer.validated_data['password'])
        user.save()
        return Response({"detail": "Password has been set successfully."})


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

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        # Ensure consistent response format
        if isinstance(response.data, list):
            response.data = {
                'count': len(response.data),
                'results': response.data
            }
        return response


# Authentication Views
class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    throttle_classes = [UserRateThrottle]

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
            return Response(
                {"detail": "Refresh token is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"detail": "Successfully logged out"})
        except TokenError:
            return Response({"detail": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            return Response({"detail": "Logout failed"}, status=status.HTTP_400_BAD_REQUEST)

class LogoutAllView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    throttle_classes = [UserRateThrottle]

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
        return Response({"detail": "Successfully logged out from all devices"})


class SetPasswordView(generics.GenericAPIView):
    serializer_class = SetPasswordSerializer
    permission_classes = [AllowAny]
    throttle_classes = [AnonRateThrottle]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"detail": "Password has been set successfully."})


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
@permission_classes([RoleBasedPermission])
def get_content_types(request):
    """Get all content types for objects dropdown"""
    ALLOWED_MODEL = [
        # accounts
        'role', 'rolepermission', 'user',

        # communications
        'emailtemplate', 'smstemplate', 'emailsignature', 'smsmessage',
        'emailmessage', 'communicationlog', 'lead', 'leadactivity',
        'supportticket', 'ticketresponse', 'ticketescalation',

        # finances
        'bank', 'bankaccount', 'itemcategory', 'invoice', 'financeitem',
        'payment', 'mpesapayment', 'bill', 'billitem', 'billpayment',
        'expense', 'creditnote', 'receivable', 'commission',

        # human_resources
        'joblevel', 'jobposition', 'department', 'contract', 'earning',
        'deduction', 'bonus', 'salaryadvance', 'penalty', 'attendance',
        'leaveapplication', 'leavetracker', 'leaveapprovalworkflow',
        'holiday', 'workingday',

        # parcels
        'delivery', 'offload', 'parcel', 'item', 'parceltracking',
        'collection',

        # people
        'contact',

        # route_management
        'location', 'station', 'destination', 'route',

        # vehicle_managements
        'vehiclecategory', 'vehicle'
    ]

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
            if ct.model in ALLOWED_MODEL
        ]
        return Response(data)
    except Exception as e:
        return Response(
            {"error": f"Failed to fetch content types: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


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
    return Response(permission_options)


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
        return Response(counts_dict)
    except Exception as e:
        return Response(
            {"error": f"Failed to get role user counts: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


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
        return Response(counts_dict)
    except Exception as e:
        return Response(
            {"error": f"Failed to get specific role user counts: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


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
        return Response(
            {'detail': 'Account and email are required'},
            status=status.HTTP_400_BAD_REQUEST
        )

    user = get_user_by_email(email)

    if user:
        reset_link = build_password_reset_link(user=user, request=request)
        send_password_reset_link_task.delay(user_id=user.id, reset_link=reset_link, password=None)

    return Response(
        {'detail': f'A reset link has been sent to {email}'}
    )


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