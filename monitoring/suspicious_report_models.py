from django.db import models

class SuspiciousContentReport(models.Model):
    reporter_name = models.CharField(max_length=255, blank=True)
    reporter_email = models.EmailField(blank=True)
    platform = models.CharField(max_length=100)
    url = models.URLField()
    description = models.TextField()
    category = models.CharField(max_length=100)
    evidence = models.FileField(upload_to='uploads/evidence/', blank=True, null=True)
    date_reported = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.platform} - {self.url} - {self.category}"
