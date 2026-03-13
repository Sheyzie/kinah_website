from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from django.shortcuts import get_object_or_404
from typing import Any


from .models import Vehicle, Dispatch
from .serializers import (
    VehicleSerializer, DispatchCreateSerializer, 
    DispatchListDetailSerializer, DispatchUpdateSerializer
)

import logging
logger = logging.getLogger(__name__)

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


class VehicleViewSet(BaseAPIView):
    serializer_class = VehicleSerializer
    permission_classes = [IsAdminUser]
    queryset = Vehicle.objects.all()

    # def get_queryset(self):
    #     user = self.request.user
    #     if user.is_staff: # TODO: set accurate permission
    #         return Vehicle.objects.all()
    #     return Vehicle.objects.filter(dispatcher=user)


class DispatchViewSet(BaseAPIView):
    serializer_class = DispatchListDetailSerializer
    permission_classes = [IsAdminUser]
    queryset = Dispatch.objects.all()

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'patial_update']:
            return DispatchCreateSerializer
        return super().get_serializer_class()

    # def get_queryset(self):
    #     user = self.request.user
    #     if user.is_staff: # TODO: set accurate permission
    #         return Dispatch.objects.all()
    #     return Dispatch.objects.filter(dispatcher=user)

    # def perform_create(self, serializer):
    #     serializer.save(user=self.request.user)

    @action(detail=True, methods=["put"], permission_classes=[IsAdminUser])
    def update_status(self, request, pk=None):
        order = self.get_object()

        serializer = DispatchUpdateSerializer(
            data=request.data,
            context={"request": request}
        )

        serializer.is_valid(raise_exception=True)

        serializer.update_status(order)

        return self.success(
            message="Dispatch status updated successfully"
        )
    
    def update(self, request, *args, **kwargs):
        return self.failure(
            message="Invalid update route for dispatch",
            code=405
        )
    



