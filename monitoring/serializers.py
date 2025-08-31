from rest_framework import serializers
from django.contrib.auth.models import User
from .models import (
    Alert, Report, ContentAnalysis, GeographicData,
    PlatformAnalytics, ChatMessage, UserSettings, FacebookPost,
    ContentModelAnalysis
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

class ContentModelAnalysisSerializer(serializers.ModelSerializer):
    """
    Serializer for the ContentModelAnalysis model
    """
    post_id = serializers.CharField(source='post.post_id', read_only=True)
    post_text = serializers.CharField(source='post.text', read_only=True)
    
    class Meta:
        model = ContentModelAnalysis
        fields = (
            'id', 'post', 'post_id', 'post_text', 'analysis_type', 
            'is_harmful', 'confidence', 'severity', 'category',
            'explanation', 'detected_keywords', 'raw_response', 
            'created_at'
        )
        read_only_fields = ('id', 'created_at')

class ContentModelAnalysisSummarySerializer(serializers.ModelSerializer):
    """
    Simplified serializer for ContentModelAnalysis model (for list views)
    """
    post_id = serializers.CharField(source='post.post_id', read_only=True)
    
    class Meta:
        model = ContentModelAnalysis
        fields = (
            'id', 'post_id', 'analysis_type', 'is_harmful', 
            'confidence', 'severity', 'created_at'
        )
        read_only_fields = ('id', 'created_at')

class ContentModelAnalysisSummarySerializer(serializers.Serializer):
    """
    Serializer for summarizing content model analysis results
    """
    total_posts = serializers.IntegerField()
    analyzed_posts = serializers.IntegerField()
    suspicious_posts = serializers.IntegerField()
    safe_posts = serializers.IntegerField()
    analysis_date = serializers.DateTimeField()

class PasswordResetRequestSerializer(serializers.Serializer):
    """
    Serializer for password reset request
    """
    email = serializers.EmailField(help_text="User's email address")

class PasswordResetSerializer(serializers.Serializer):
    """
    Serializer for password reset
    """
    token = serializers.CharField(help_text="Password reset token")
    password = serializers.CharField(help_text="New password", min_length=8)
    password_confirm = serializers.CharField(help_text="Password confirmation")

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs

class EmailVerificationSerializer(serializers.Serializer):
    """
    Serializer for email verification
    """
    token = serializers.CharField(help_text="Email verification token")