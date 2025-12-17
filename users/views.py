from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.mail import send_mail
from django.conf import settings
import logging

from .serializers import (
    UserRegistrationSerializer, 
    UserProfileSerializer,
    PasswordResetSerializer,
    SetNewPasswordSerializer
)

User = get_user_model()
logger = logging.getLogger(__name__)

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
                token = default_token_generator.make_token(user)
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                
                frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:5173')
                # Use a standard clean URL structure
                reset_link = f"{frontend_url}/reset-password?uid={uid}&token={token}"
                
                try:
                    send_mail(
                        'Password Reset Request - ETS2 Mods',
                        f'Click the following link to reset your password: {reset_link}',
                        settings.DEFAULT_FROM_EMAIL,
                        [email],
                        fail_silently=False,
                    )
                except Exception as e:
                    logger.error(f"Failed to send password reset email to {email}: {e}")
                    # In production, do not reveal if email sending failed to prevent enumeration,
                    # but for debugging it's useful to know.
            
            # Always return the same message to prevent email enumeration
            return Response({'message': 'If an account with this email exists, a reset link has been sent.'})
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PasswordResetConfirmView(generics.GenericAPIView):
    serializer_class = SetNewPasswordSerializer
    permission_classes = (permissions.AllowAny,)

    def patch(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({'message': 'Password reset successful'})