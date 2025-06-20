from django.shortcuts import render

# Create your views here.
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from .serializers import SuspiciousContentReportSerializer
from .models import SuspiciousContentReport
from drf_yasg.utils import swagger_auto_schema

@swagger_auto_schema(method='post', request_body=SuspiciousContentReportSerializer, responses={201: 'Report submitted successfully', 400: 'Invalid data'})
@api_view(["POST"])
@permission_classes([AllowAny])  # Explicitly allow any (no authentication)
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
            content_type=serializer.validated_data["content_type"],
            platform=serializer.validated_data["platform"],
            url=serializer.validated_data["url"],
            urgency_level=serializer.validated_data["urgency_level"],
            description=serializer.validated_data["description"],
            evidence=evidence,
        )
        return Response({"success": True, "message": "Report submitted successfully."}, status=status.HTTP_201_CREATED)
    return Response({"success": False, "message": "Invalid data.", "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

@swagger_auto_schema(method='get', responses={200: SuspiciousContentReportSerializer(many=True)})
@api_view(["GET"])
@permission_classes([IsAdminUser])  # Only allow admin users to view reports
def suspicious_content_report_list(request):
    reports = SuspiciousContentReport.objects.all().order_by('-date_reported')
    serializer = SuspiciousContentReportSerializer(reports, many=True)
    return Response(serializer.data)


