from rest_framework import serializers

class SuspiciousContentReportSerializer(serializers.Serializer):
    reporter_name = serializers.CharField(required=False, allow_blank=True)
    reporter_email = serializers.EmailField(required=False, allow_blank=True)
    content_type = serializers.CharField(required=True)
    platform = serializers.CharField(required=True)
    url = serializers.URLField(required=True)
    urgency_level = serializers.CharField(required=True)
    description = serializers.CharField(required=True)
    evidence = serializers.FileField(required=False, allow_null=True)
    date_reported = serializers.DateTimeField(read_only=True)



class AnalysisSerializer(serializers.Serializer):
    """This is takes a text and send to the fastapi for analysis"""
    ANALYSIS_CHOICES = [
        ('hate_speech', 'Hate Speech Only'),
        ('misinformation', 'Misinformation Only'),
    ]

    text = serializers.CharField(required=True, allow_blank=False)
    analysis_type = serializers.ChoiceField(
        choices=ANALYSIS_CHOICES,
        default='hate_speech',
        required=False,
        help_text="Select the type of analysis to perform"
    )

    def validate_text(self, value):
        """Additional validation for text field"""
        if len(value.strip()) == 0:
            raise serializers.ValidationError("Text cannot be empty or only whitespace")
        return value.strip()


class DateRangeSerializer(serializers.Serializer):
    start_date = serializers.DateTimeField()
    end_date = serializers.DateTimeField()


class FiltersSerializer(serializers.Serializer):
    platforms = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        default=list
    )
    severity_levels = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        default=list
    )
    content_types = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        default=list
    )
    locations = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        default=list
    )


class DashboardReportRequestSerializer(serializers.Serializer):
    REPORT_TYPE_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('custom', 'Custom'),
    ]

    report_type = serializers.ChoiceField(
        choices=REPORT_TYPE_CHOICES,
        default='daily'
    )
    date_range = DateRangeSerializer(required=False)
    filters = FiltersSerializer(required=False)


class PlatformBreakdownSerializer(serializers.Serializer):
    platform = serializers.CharField()
    total_posts = serializers.IntegerField()
    hate_speech = serializers.IntegerField()
    misinformation = serializers.IntegerField()
    safe = serializers.IntegerField()


class SeverityDistributionSerializer(serializers.Serializer):
    severity = serializers.CharField()
    count = serializers.IntegerField()
    percentage = serializers.FloatField()


class TopKeywordSerializer(serializers.Serializer):
    keyword = serializers.CharField()
    frequency = serializers.IntegerField()
    severity = serializers.CharField()


class LocationInsightSerializer(serializers.Serializer):
    location = serializers.CharField()
    total_posts = serializers.IntegerField()
    risk_level = serializers.CharField()
    common_issues = serializers.ListField(child=serializers.CharField())


class TrendSerializer(serializers.Serializer):
    date = serializers.DateField()
    hate_speech_count = serializers.IntegerField()
    misinformation_count = serializers.IntegerField()
    average_risk_score = serializers.FloatField()


class DashboardReportSerializer(serializers.Serializer):
    report_id = serializers.CharField()
    generated_at = serializers.DateTimeField()
    date_range = DateRangeSerializer()
    summary = serializers.DictField()
    platform_breakdown = PlatformBreakdownSerializer(many=True)
    severity_distribution = SeverityDistributionSerializer(many=True)
    top_keywords = TopKeywordSerializer(many=True)
    location_insights = LocationInsightSerializer(many=True)
    trends = TrendSerializer(many=True)