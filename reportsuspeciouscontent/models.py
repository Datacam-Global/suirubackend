from django.db import models

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
    date_reported = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.platform} - {self.url} - {self.content_type}"
