from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.conf import settings
import jwt
from datetime import timedelta
from django.utils import timezone
from .serializers import UserSerializer
from .models import UserSettings

def generate_token(user, token_type='email_verification', expiry=24):
    """Generate a JWT token for email verification"""
    payload = {
        'user_id': user.id,
        'token_type': token_type,
        'exp': timezone.now() + timedelta(hours=expiry)
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')

class RegisterView(generics.CreateAPIView):
    """
    API endpoint for user registration.
    
    Parameters:
    - username: string (required)
    - email: string (required)
    - password: string (required)
    - first_name: string (optional)
    - last_name: string (optional)
    
    Returns:
    - 201: User created successfully
    - 400: Invalid input data
    """
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = UserSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            try:
                # Validate password
                validate_password(request.data.get('password'))
                
                # Create user
                user = serializer.save()
                user.set_password(request.data.get('password'))
                user.save()
                
                # Create user settings
                UserSettings.objects.create(user=user)
                
                # Generate verification token and send email
                token = generate_token(user)
                verification_url = f"{settings.FRONTEND_URL}/verify-email?token={token}"
                
                send_mail(
                    'Verify Your Email',
                    f'Click the following link to verify your email: {verification_url}',
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                    fail_silently=False,
                )
                
                return Response({
                    'user': serializer.data,
                    'message': 'User created successfully. Please check your email for verification.'
                }, status=status.HTTP_201_CREATED)
            except ValidationError as e:
                return Response({
                    'error': e.messages
                }, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CustomTokenObtainPairView(TokenObtainPairView):
    """
    API endpoint for obtaining JWT tokens.
    
    Parameters:
    - username: string (required)
    - password: string (required)
    
    Returns:
    - 200: Tokens generated successfully
    - 401: Invalid credentials
    """
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            user = User.objects.get(username=request.data['username'])
            user_data = UserSerializer(user).data
            response.data['user'] = user_data
        return response 