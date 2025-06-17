from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# Add unique constraint to User model's email field
User._meta.get_field('email')._unique = True

class Alert(models.Model):
    SEVERITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    STATUS_CHOICES = [
        ('new', 'New'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    source = models.CharField(max_length=100)
    location = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    def __str__(self):
        return f"{self.title} - {self.severity}"

class Report(models.Model):
    REPORT_TYPE_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('custom', 'Custom'),
    ]

    title = models.CharField(max_length=200)
    content = models.TextField()
    report_type = models.CharField(max_length=20, choices=REPORT_TYPE_CHOICES)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    is_public = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.title} - {self.report_type}"

class ContentAnalysis(models.Model):
    content_type = models.CharField(max_length=50)  # text, image, video, etc.
    content_url = models.URLField()
    analysis_result = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    confidence_score = models.FloatField()
    tags = models.JSONField(default=list)
    
    def __str__(self):
        return f"{self.content_type} Analysis - {self.created_at}"

class GeographicData(models.Model):
    location_name = models.CharField(max_length=200)
    latitude = models.FloatField()
    longitude = models.FloatField()
    data_type = models.CharField(max_length=50)  # alert, report, analysis
    data_id = models.IntegerField()  # ID of the related object
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.location_name} - {self.data_type}"

class PlatformAnalytics(models.Model):
    platform_name = models.CharField(max_length=100)
    metrics = models.JSONField()
    timestamp = models.DateTimeField(auto_now_add=True)
    period = models.CharField(max_length=20)  # daily, weekly, monthly
    
    def __str__(self):
        return f"{self.platform_name} - {self.period}"

class ChatMessage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    is_bot = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.timestamp}"

class UserSettings(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    theme = models.CharField(max_length=20, default='dark')
    notifications_enabled = models.BooleanField(default=True)
    email_notifications = models.BooleanField(default=True)
    email_verified = models.BooleanField(default=False)
    dashboard_layout = models.JSONField(default=dict)
    
    def __str__(self):
        return f"{self.user.username}'s Settings"

class FacebookPost(models.Model):
    """
    Model to store Facebook post data from Data365 API integration
    """
    post_id = models.CharField(max_length=50, unique=True)
    created_time = models.CharField(max_length=50)
    timestamp = models.BigIntegerField()
    post_type = models.CharField(max_length=50)
    text = models.TextField(blank=True)
    text_lang = models.CharField(max_length=10, blank=True)
    text_tagged_users = models.JSONField(default=list)
    text_tags = models.JSONField(default=list)
    attached_link = models.URLField(blank=True)
    attached_link_description = models.TextField(blank=True)
    attached_image_url = models.URLField(blank=True)
    attached_image_url_s3 = models.URLField(blank=True)
    attached_image_content = models.TextField(blank=True)
    attached_medias_id = models.JSONField(default=list)
    attached_medias_preview_url = models.JSONField(default=list)
    attached_medias_preview_url_s3 = models.JSONField(default=list)
    attached_medias_preview_content = models.JSONField(default=list)
    attached_post_id = models.CharField(max_length=50, blank=True)
    attached_video_preview_url = models.URLField(blank=True)
    attached_video_preview_url_s3 = models.URLField(blank=True)
    attached_video_url = models.URLField(blank=True)
    post_screenshot = models.URLField(blank=True)
    reactions_like_count = models.IntegerField(default=0)
    reactions_love_count = models.IntegerField(default=0)
    reactions_haha_count = models.IntegerField(default=0)
    reactions_wow_count = models.IntegerField(default=0)
    reactions_sad_count = models.IntegerField(default=0)
    reactions_angry_count = models.IntegerField(default=0)
    reactions_support_count = models.IntegerField(default=0)
    reactions_total_count = models.IntegerField(default=0)
    comments_count = models.IntegerField(default=0)
    shares_count = models.IntegerField(default=0)
    video_view_count = models.IntegerField(default=0)
    video_duration = models.IntegerField(default=0)
    overlay_text = models.TextField(blank=True)
    fact_checks = models.JSONField(default=list)
    owner_id = models.CharField(max_length=50)
    owner_username = models.CharField(max_length=100)
    owner_full_name = models.CharField(max_length=200)
    group_id = models.CharField(max_length=50, blank=True)
    recommends = models.BooleanField(default=False)
    tagged_location_id = models.CharField(max_length=50, blank=True)
    post_location_id = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.owner_username} - {self.post_id}"
