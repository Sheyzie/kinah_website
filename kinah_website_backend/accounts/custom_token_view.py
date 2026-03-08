from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.permissions import AllowAny
from accounts.throttling import LoginRateThrottle

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    permission_classes=[AllowAny]

    def validate(self, attrs):
        # Use email instead of username
        attrs['username'] = attrs.get('email', '')  # Map email to username field
        return super().validate(attrs)

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
    permission_classes=[AllowAny]
    throttle_classes = [LoginRateThrottle]