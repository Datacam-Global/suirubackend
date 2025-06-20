from rest_framework import serializers
from django.contrib.auth.models import User
from .models import (
    Alert, Report, ContentAnalysis, GeographicData,
    PlatformAnalytics, ChatMessage, UserSettings, FacebookPost
)
from reportsuspeciouscontent.models import SuspiciousContentReport

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    password_confirm = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'password', 'password_confirm')
        read_only_fields = ('id',)

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        
        # Check for duplicate email
        email = attrs.get('email')
        if email and User.objects.filter(email=email).exists():
            raise serializers.ValidationError({"email": "A user with this email already exists."})
        
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user

class AlertSerializer(serializers.ModelSerializer):
    assigned_to = UserSerializer(read_only=True)
    
    class Meta:
        model = Alert
        fields = '__all__'

class ReportSerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True)
    
    class Meta:
        model = Report
        fields = '__all__'

class ContentAnalysisSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContentAnalysis
        fields = '__all__'

class GeographicDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = GeographicData
        fields = '__all__'

class PlatformAnalyticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlatformAnalytics
        fields = '__all__'

class ChatMessageSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = ChatMessage
        fields = '__all__'

class UserSettingsSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = UserSettings
        fields = '__all__'

class FacebookPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = FacebookPost
        fields = '__all__'
        
class FacebookAPIResponseSerializer(serializers.Serializer):
    """
    Serializer for Facebook API response format matching Data365 structure
    """
    data = FacebookPostSerializer()
    error = serializers.CharField(allow_null=True, default=None)
    status = serializers.CharField(default="ok")