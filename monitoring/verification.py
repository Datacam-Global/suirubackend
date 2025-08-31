from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings
from django.utils.crypto import get_random_string
from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.decorators import api_view, permission_classes
from django.utils import timezone
from datetime import timedelta
import jwt
from .serializers import (
    UserSerializer, 
    PasswordResetRequestSerializer, 
    PasswordResetSerializer, 
    EmailVerificationSerializer
)

def generate_token(user, token_type='email_verification', expiry=24):
    """Generate a JWT token for email verification or password reset"""
    payload = {
        'user_id': user.id,
        'token_type': token_type,
        'exp': timezone.now() + timedelta(hours=expiry)
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')

def verify_token(token, token_type):
    """Verify a JWT token"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        if payload['token_type'] != token_type:
            return None
        return User.objects.get(id=payload['user_id'])
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, User.DoesNotExist):
        return None

class RequestPasswordResetView(generics.GenericAPIView):
    """
    API endpoint for requesting password reset.
    
    Parameters:
    - email: string (required)
    
    Returns:
    - 200: Password reset email sent
    - 400: Invalid email
    """
    serializer_class = PasswordResetRequestSerializer
    permission_classes = (AllowAny,)

    def post(self, request):
        email = request.data.get('email')
        try:
            user = User.objects.get(email=email)
            token = generate_token(user, 'password_reset', 1)  # 1 hour expiry
            
            reset_url = f"{settings.FRONTEND_URL}/reset-password?token={token}"
            
            send_mail(
                'Password Reset Request',
                f'Click the following link to reset your password: {reset_url}',
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )
            
            return Response({
                'message': 'Password reset email sent successfully'
            }, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({
                'error': 'No user found with this email address'
            }, status=status.HTTP_400_BAD_REQUEST)

class ResetPasswordView(generics.GenericAPIView):
    """
    API endpoint for resetting password.
    
    Parameters:
    - token: string (required)
    - password: string (required)
    - password_confirm: string (required)
    
    Returns:
    - 200: Password reset successful
    - 400: Invalid token or password
    """
    serializer_class = PasswordResetSerializer
    permission_classes = (AllowAny,)

    def post(self, request):
        token = request.data.get('token')
        password = request.data.get('password')
        password_confirm = request.data.get('password_confirm')

        if password != password_confirm:
            return Response({
                'error': 'Passwords do not match'
            }, status=status.HTTP_400_BAD_REQUEST)

        user = verify_token(token, 'password_reset')
        if not user:
            return Response({
                'error': 'Invalid or expired token'
            }, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(password)
        user.save()

        return Response({
            'message': 'Password reset successful'
        }, status=status.HTTP_200_OK)

class VerifyEmailView(generics.GenericAPIView):
    """
    API endpoint for verifying email.
    
    Parameters:
    - token: string (required)
    
    Returns:
    - 200: Email verified successfully
    - 400: Invalid token
    """
    serializer_class = EmailVerificationSerializer
    permission_classes = (AllowAny,)

    def post(self, request):
        token = request.data.get('token')
        user = verify_token(token, 'email_verification')
        
        if not user:
            return Response({
                'error': 'Invalid or expired token'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Create or update UserSettings to mark email as verified
        from .models import UserSettings
        settings, _ = UserSettings.objects.get_or_create(user=user)
        settings.email_verified = True
        settings.save()

        return Response({
            'message': 'Email verified successfully'
        }, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([AllowAny])
def resend_verification_email(request):
    """
    API endpoint for resending verification email.
    
    Parameters:
    - email: string (required)
    
    Returns:
    - 200: Verification email sent
    - 400: Invalid email
    """
    email = request.data.get('email')
    try:
        user = User.objects.get(email=email)
        token = generate_token(user, 'email_verification')
        
        verification_url = f"{settings.FRONTEND_URL}/verify-email?token={token}"
        
        send_mail(
            'Verify Your Email',
            f'Click the following link to verify your email: {verification_url}',
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=False,
        )
        
        return Response({
            'message': 'Verification email sent successfully'
        }, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        return Response({
            'error': 'No user found with this email address'
        }, status=status.HTTP_400_BAD_REQUEST) 