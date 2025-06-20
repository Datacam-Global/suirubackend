from django.contrib import admin
from .models import SuspiciousContentReport
# Register your models here.

@admin.register(SuspiciousContentReport)
class SuspiciousContentReportAdmin(admin.ModelAdmin):
    list_display = ('platform', 'url', 'content_type', 'reporter_email', 'date_reported')
    search_fields = ('platform', 'url', 'content_type', 'reporter_email', 'description')
    list_filter = ('platform', 'content_type', 'date_reported')
