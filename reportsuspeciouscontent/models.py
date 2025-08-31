from django.db import models
from django.utils import timezone


class SuspiciousContentReport(models.Model):
    CONTENT_TYPE_CHOICES = [
        ('misinformation', 'Misinformation'),
        ('hatespeech', 'Hate Speech'),
        ('harassment', 'Harassment'),
        ('spam', 'Spam'),
        ('fake', 'Fake'),
        ('news', 'News'),
        ('other', 'Other'),
    ]

    PLATFORM_CHOICES = [
        ('facebook', 'Facebook'),
        ('youtube', 'YouTube'),
        ('tiktok', 'TikTok'),
        ('whatsapp', 'WhatsApp'),
        ('twitter', 'Twitter'),
        ('other', 'Other'),
    ]

    URGENCY_LEVEL_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    reporter_name = models.CharField(max_length=255, blank=True, null=True)
    reporter_email = models.EmailField(blank=True, null=True)
    content_type = models.CharField(max_length=20, choices=CONTENT_TYPE_CHOICES)
    platform = models.CharField(max_length=100, choices=PLATFORM_CHOICES)
    url = models.URLField()
    urgency_level = models.CharField(max_length=10, choices=URGENCY_LEVEL_CHOICES)
    description = models.TextField()
    evidence = models.FileField(upload_to='uploads/evidence/', blank=True, null=True)
    date_reported = models.DateTimeField(
        default=timezone.now,
        help_text="When the content was reported/detected"
    )
    confidence_score = models.FloatField(
        default=0.0,
        help_text="AI confidence score for the detection (0.0-1.0)"
    )
    location = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Geographic location (Cameroon city/region)"
    )

    # Additional tracking
    post_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Original post ID from the platform"
    )
    user_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="User ID who posted the content"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'suspicious_content_reports'
        ordering = ['-date_reported']
        indexes = [
            models.Index(fields=['date_reported']),
            models.Index(fields=['content_type']),
            models.Index(fields=['urgency_level']),
            models.Index(fields=['platform']),
            models.Index(fields=['location']),
        ]

    def __str__(self):
        return f"{self.content_type} - {self.urgency_level} - {self.platform}"

