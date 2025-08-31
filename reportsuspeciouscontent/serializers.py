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


