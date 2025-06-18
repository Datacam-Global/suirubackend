from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from .suspicious_report_serializers import SuspiciousContentReportSerializer
from .suspicious_report_models import SuspiciousContentReport

@api_view(["POST"])
@permission_classes([])  # Explicitly allow any (no authentication)
@parser_classes([MultiPartParser, FormParser, JSONParser])
def suspicious_content_report(request):
    data = request.data.copy()
    data["date_reported"] = timezone.now()
    serializer = SuspiciousContentReportSerializer(data=data)
    if serializer.is_valid():
        evidence = request.FILES.get("evidence")
        report = SuspiciousContentReport.objects.create(
            reporter_name=serializer.validated_data.get("reporter_name", ""),
            reporter_email=serializer.validated_data.get("reporter_email", ""),
            platform=serializer.validated_data["platform"],
            url=serializer.validated_data["url"],
            description=serializer.validated_data["description"],
            category=serializer.validated_data["category"],
            evidence=evidence,
        )
        return Response({"success": True, "message": "Report submitted successfully."}, status=status.HTTP_201_CREATED)
    return Response({"success": False, "message": "Invalid data.", "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

@api_view(["GET"])
@permission_classes([IsAdminUser])
def suspicious_content_report_list(request):
    reports = SuspiciousContentReport.objects.all().order_by('-date_reported')
    serializer = SuspiciousContentReportSerializer(reports, many=True)
    return Response(serializer.data)
