from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from django.shortcuts import get_object_or_404

from .models import Address, Order, Coupon, Payment
from .serializers import (
    AddressSerializer,
    OrderListSerializer,
    OrderDetailSerializer,
    OrderCreateUpdateSerializer,
    CouponSerializer,
    CouponValidateSerializer,
    PaymentSerializer,
    OrderStatusUpdateSerializer
)


class BaseAPIView(viewsets.ModelViewSet):
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

        return self.success(
            data=serializer.data,
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


class AddressViewSet(BaseAPIView):
    serializer_class = AddressSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class OrderViewSet(BaseAPIView):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if user.is_staff: # TODO: set accurate permission
            return Order.objects.all()

        return Order.objects.filter(user=user)

    def get_serializer_class(self):
        if self.action == "list":
            return OrderListSerializer

        if self.action == "retrieve":
            return OrderDetailSerializer

        if self.action in ["create", "update", "partial_update"]:
            return OrderCreateUpdateSerializer

        return OrderDetailSerializer
    
    @action(detail=True, methods=["post"], permission_classes=[IsAdminUser])
    def update_status(self, request, pk=None):
        order = self.get_object()

        serializer = OrderStatusUpdateSerializer(
            data=request.data,
            context={"request": request}
        )

        serializer.is_valid(raise_exception=True)

        serializer.update_status(order)

        return self.success(
            message="Order status updated successfully"
        )
    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        user = request.user
        has_access = user.is_authenticated and (user.is_superuser or (hasattr(user, 'role') and user.role.is_admin))
        if instance.status == 'pending' or has_access:
            return super().update(request, *args, **kwargs)
        
        return self.failure(
            message=f"Cannot update a processed order",
            code=403
        )
    

class CouponViewSet(BaseAPIView):
    queryset = Coupon.objects.all()
    serializer_class = CouponSerializer
    permission_classes = [IsAdminUser]

    @action(detail=False, methods=["post"], permission_classes=[AllowAny])
    def validate_coupon(self, request):

        serializer = CouponValidateSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        return self.success(
            message='Coupon is valid',
            data=serializer.data,
            code=200
        )


class PaymentViewSet(BaseAPIView):
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if user.is_staff:
            return Payment.objects.all()

        return Payment.objects.filter(order__user=user)
    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        user = request.user
        has_access = user.is_authenticated and (user.is_superuser or (hasattr(user, 'role') and user.role.is_admin))
        if has_access:
            return super().update(request, *args, **kwargs)
        
        return self.failure(
            message=f"You are not authorised to carry out this action",
            code=403
        )

    
