from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import (
    UserRegistrationSerializer, 
    UserProfileSerializer,
    PasswordResetSerializer,
    SetNewPasswordSerializer
)

User = get_user_model()

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = UserRegistrationSerializer

class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        return self.request.user

class PasswordResetRequestView(APIView):
    permission_classes = (permissions.AllowAny,)
    
    def post(self, request):
        serializer = PasswordResetSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            user = User.objects.filter(email=email).first()
            if user:
                # In real app: Send email with token using PasswordResetTokenGenerator
                # link = reverse('password-reset-confirm', kwargs={'uidb64': ..., 'token': ...})
                pass 
            return Response({'message': 'If email exists, reset link sent.'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PasswordResetConfirmView(generics.GenericAPIView):
    serializer_class = SetNewPasswordSerializer
    permission_classes = (permissions.AllowAny,)

    def patch(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({'message': 'Password reset successful'})