from rest_framework import serializers

class SuspiciousContentReportSerializer(serializers.Serializer):
    reporter_name = serializers.CharField(required=False, allow_blank=True)
    reporter_email = serializers.EmailField(required=False, allow_blank=True)
    platform = serializers.CharField(required=True)
    url = serializers.URLField(required=True)
    description = serializers.CharField(required=True)
    category = serializers.CharField(required=True)
    evidence = serializers.FileField(required=False, allow_null=True)
    date_reported = serializers.DateTimeField(read_only=True)
