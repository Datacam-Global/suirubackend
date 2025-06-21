from django.contrib import admin
from .models import (
    Alert, Report, ContentAnalysis, GeographicData,
    PlatformAnalytics, ChatMessage, UserSettings, FacebookPost,RegisteredPlatform
)


@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display = ('title', 'severity', 'status', 'created_at', 'assigned_to')
    list_filter = ('severity', 'status', 'created_at')
    search_fields = ('title', 'description', 'source')

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('title', 'report_type', 'created_by', 'created_at', 'is_public')
    list_filter = ('report_type', 'created_at', 'is_public')
    search_fields = ('title', 'content')

@admin.register(ContentAnalysis)
class ContentAnalysisAdmin(admin.ModelAdmin):
    list_display = ('content_type', 'confidence_score', 'created_at')
    list_filter = ('content_type', 'created_at')
    search_fields = ('content_url', 'tags')

@admin.register(GeographicData)
class GeographicDataAdmin(admin.ModelAdmin):
    list_display = ('location_name', 'data_type', 'created_at')
    list_filter = ('data_type', 'created_at')
    search_fields = ('location_name',)

@admin.register(PlatformAnalytics)
class PlatformAnalyticsAdmin(admin.ModelAdmin):
    list_display = ('platform_name', 'period', 'timestamp')
    list_filter = ('platform_name', 'period', 'timestamp')
    search_fields = ('platform_name',)

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_bot', 'timestamp')
    list_filter = ('is_bot', 'timestamp')
    search_fields = ('message', 'user__username')

@admin.register(UserSettings)
class UserSettingsAdmin(admin.ModelAdmin):
    list_display = ('user', 'theme', 'notifications_enabled')
    list_filter = ('theme', 'notifications_enabled')
    search_fields = ('user__username',)

@admin.register(FacebookPost)
class FacebookPostAdmin(admin.ModelAdmin):
    list_display = ('post_id', 'owner_username', 'owner_full_name', 'post_type', 'reactions_total_count', 'created_time')
    list_filter = ('post_type', 'text_lang', 'created_at')
    search_fields = ('post_id', 'owner_username', 'owner_full_name', 'text')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('post_id', 'created_time', 'timestamp', 'post_type')
        }),
        ('Content', {
            'fields': ('text', 'text_lang', 'text_tagged_users', 'text_tags')
        }),
        ('Attachments', {
            'fields': ('attached_link', 'attached_link_description', 'attached_image_url', 'attached_image_url_s3', 'attached_image_content'),
            'classes': ('collapse',)
        }),
        ('Media', {
            'fields': ('attached_medias_id', 'attached_medias_preview_url', 'attached_medias_preview_url_s3', 'attached_medias_preview_content'),
            'classes': ('collapse',)
        }),
        ('Video', {
            'fields': ('attached_video_preview_url', 'attached_video_preview_url_s3', 'attached_video_url', 'video_view_count', 'video_duration'),
            'classes': ('collapse',)
        }),
        ('Engagement', {
            'fields': ('reactions_like_count', 'reactions_love_count', 'reactions_haha_count', 'reactions_wow_count', 
                      'reactions_sad_count', 'reactions_angry_count', 'reactions_support_count', 'reactions_total_count',
                      'comments_count', 'shares_count')
        }),
        ('Owner Information', {
            'fields': ('owner_id', 'owner_username', 'owner_full_name', 'group_id')
        }),
        ('Location & Metadata', {
            'fields': ('tagged_location_id', 'post_location_id', 'recommends', 'overlay_text', 'fact_checks'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )



@admin.register(RegisteredPlatform)
class RegisteredPlatformAdmin(admin.ModelAdmin):
    list_display = ('name', 'display_name', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('name', 'display_name')