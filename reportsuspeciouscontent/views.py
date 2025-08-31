import logging
from concurrent.futures.thread import ThreadPoolExecutor
from datetime import timedelta

import requests
from django.db.models import Count
from django.utils import timezone
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status, views, permissions
# Create your views here.
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response

from .models import SuspiciousContentReport
from .serializers import SuspiciousContentReportSerializer, AnalysisSerializer

logger = logging.getLogger(__name__)

@swagger_auto_schema(method='post', request_body=SuspiciousContentReportSerializer,
                     responses={201: 'Report submitted successfully', 400: 'Invalid data'})
@api_view(["POST"])
@permission_classes([AllowAny])
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
    return Response({"success": False, "message": "Invalid data.", "errors": serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(method='get', responses={200: SuspiciousContentReportSerializer(many=True)})
@api_view(["GET"])
@permission_classes([IsAdminUser])
def suspicious_content_report_list(request):
    reports = SuspiciousContentReport.objects.all().order_by('-date_reported')
    serializer = SuspiciousContentReportSerializer(reports, many=True)
    return Response(serializer.data)


@swagger_auto_schema(
    method='get',
    manual_parameters=[
        openapi.Parameter(
            'period',
            openapi.IN_QUERY,
            description="Time period for the report (24h, 7d, 30d, 1y)",
            type=openapi.TYPE_STRING,
            default='24h'
        ),
        openapi.Parameter(
            'content_types',
            openapi.IN_QUERY,
            description="Comma-separated content types to filter (e.g., 'hatespeech,misinformation')",
            type=openapi.TYPE_STRING,
            required=False
        ),
    ],
    responses={
        200: openapi.Response(
            description="Report data",
            examples={
                "application/json": {
                    "success": True,
                    "report": {
                        "period": "24h",
                        "total_reports": 45,
                        "content_type_breakdown": {
                            "hatespeech": 20,
                            "misinformation": 15,
                            "harassment": 10
                        },
                        "platform_breakdown": {
                            "facebook": 18,
                            "twitter": 12,
                            "youtube": 10,
                            "tiktok": 5
                        },
                        "urgency_breakdown": {
                            "critical": 5,
                            "high": 15,
                            "medium": 20,
                            "low": 5
                        },
                        "daily_trend": [
                            {"date": "2024-01-01", "count": 12},
                            {"date": "2024-01-02", "count": 15}
                        ],
                        "report_generated_at": "2024-01-02T10:30:00Z"
                    }
                }
            }
        )
    }
)
@api_view(["GET"])
def generate_suspicious_content_report(request):
    """
    Generate a comprehensive report of suspicious content detected by the system.

    Query Parameters:
    - period: Time period (24h, 7d, 30d, 1y) - default: 24h
    - content_types: Comma-separated content types to filter (optional)
    """

    # Get query parameters
    period = request.GET.get('period', '24h')
    content_types_param = request.GET.get('content_types', '')

    # Calculate date range based on period
    now = timezone.now()
    if period == '24h':
        start_date = now - timedelta(hours=24)
        period_label = "Last 24 hours"
    elif period == '7d':
        start_date = now - timedelta(days=7)
        period_label = "Last 7 days"
    elif period == '30d':
        start_date = now - timedelta(days=30)
        period_label = "Last 30 days"
    elif period == '1y':
        start_date = now - timedelta(days=365)
        period_label = "Last year"
    else:
        return Response(
            {"success": False, "message": "Invalid period. Use 24h, 7d, 30d, or 1y"},
            status=status.HTTP_400_BAD_REQUEST
        )

    base_query = SuspiciousContentReport.objects.filter(date_reported__gte=start_date)

    if content_types_param:
        content_types = [ct.strip() for ct in content_types_param.split(',')]
        base_query = base_query.filter(content_type__in=content_types)

    total_reports = base_query.count()

    # Content type breakdown
    content_type_breakdown = dict(
        base_query.values('content_type')
        .annotate(count=Count('id'))
        .values_list('content_type', 'count')
    )

    platform_breakdown = dict(
        base_query.values('platform')
        .annotate(count=Count('id'))
        .values_list('platform', 'count')
    )

    urgency_breakdown = dict(
        base_query.values('urgency_level')
        .annotate(count=Count('id'))
        .values_list('urgency_level', 'count')
    )

    daily_trend = []
    if period != '24h':
        # Get daily counts for the period
        days_back = 7 if period == '7d' else (30 if period == '30d' else 365)
        for i in range(days_back):
            date = (now - timedelta(days=i)).date()
            count = base_query.filter(date_reported__date=date).count()
            daily_trend.append({
                "date": date.strftime('%Y-%m-%d'),
                "count": count
            })
        daily_trend.reverse()

    hourly_trend = []
    if period == '24h':
        for i in range(24):
            hour_start = now - timedelta(hours=i + 1)
            hour_end = now - timedelta(hours=i)
            count = base_query.filter(
                date_reported__gte=hour_start,
                date_reported__lt=hour_end
            ).count()
            hourly_trend.append({
                "hour": hour_start.strftime('%H:00'),
                "count": count
            })
        hourly_trend.reverse()

    top_platforms = list(
        base_query.values('platform')
        .annotate(count=Count('id'))
        .order_by('-count')[:5]
    )

    high_priority_reports = base_query.filter(
        urgency_level__in=['high', 'critical']
    ).order_by('-date_reported')[:10]

    recent_high_priority = []
    for report in high_priority_reports:
        recent_high_priority.append({
            'id': report.id,
            'content_type': report.content_type,
            'platform': report.platform,
            'urgency_level': report.urgency_level,
            'url': report.url,
            'date_reported': report.date_reported.isoformat()
        })

    report_data = {
        "success": True,
        "report": {
            "period": period,
            "period_label": period_label,
            "date_range": {
                "start": start_date.isoformat(),
                "end": now.isoformat()
            },
            "total_reports": total_reports,
            "content_type_breakdown": content_type_breakdown,
            "platform_breakdown": platform_breakdown,
            "urgency_breakdown": urgency_breakdown,
            "top_platforms": top_platforms,
            "recent_high_priority_reports": recent_high_priority,
            "report_generated_at": now.isoformat()
        }
    }

    if period == '24h':
        report_data["report"]["hourly_trend"] = hourly_trend
    else:
        report_data["report"]["daily_trend"] = daily_trend

    return Response(report_data, status=status.HTTP_200_OK)


class UnifiedAnalysisAPIView(views.APIView):
    """Analyze text for hate speech and/or misinformation detection"""
    permission_classes = [permissions.AllowAny]

    HATE_SPEECH_URL = "http://84.247.168.4:8001/hate/analyze"
    MISINFORMATION_URL = "http://84.247.168.4:8001/misinformation/analyze"
    TIMEOUT = 30
    serializer_class = AnalysisSerializer

    def call_api(self, url, payload):
        """Helper method to call external APIs"""
        try:
            response = requests.post(
                url,
                json=payload,
                timeout=self.TIMEOUT,
                headers={'Content-Type': 'application/json'}
            )
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except Exception as e:
            logger.error(f"Error calling {url}: {e}")
            return {"success": False, "error": str(e)}

    @swagger_auto_schema(
        operation_summary="Analyze text for hate speech and/or misinformation",
        operation_description="Analyzes text using ML models to detect hate speech and misinformation",
        request_body=AnalysisSerializer,
        responses={
            200: openapi.Response(
                description="Analysis completed successfully",
                examples={
                    "application/json": {
                        "text": "I love Cameroon booy",
                        "hate_speech_analysis": {
                            "is_hate_speech": False,
                            "confidence": 0.0,
                            "category": "none",
                            "severity": "none",
                            "detected_keywords": [],
                            "explanation": "Clean"
                        },
                        "misinformation_analysis": {
                            "label": "verified",
                            "confidence": 0.8,
                            "severity": "low",
                            "explanation": "Content appears to be factual"
                        },
                        "timestamp": "2025-08-30T22:34:20.711373"
                    }
                }
            ),
            400: "Invalid input data",
            408: "Request timeout",
            500: "Internal server error",
            502: "Analysis service error",
            503: "Service unavailable"
        }
    )
    def post(self, request):
        """Analyze text for hate speech and/or misinformation"""
        try:
            serializer = self.serializer_class(data=request.data)
            serializer.is_valid(raise_exception=True)

            text = serializer.validated_data['text']
            analysis_type = serializer.validated_data.get('analysis_type', 'hate_speech')
            payload = {"text": text}

            calls_to_make = []

            if analysis_type in ['hate_speech']:
                calls_to_make.append(('hate_speech', self.HATE_SPEECH_URL))

            if analysis_type in ['misinformation']:
                calls_to_make.append(('misinformation', self.MISINFORMATION_URL))

            results = {}
            errors = {}

            with ThreadPoolExecutor(max_workers=2) as executor:
                future_to_type = {
                    executor.submit(self.call_api, url, payload): analysis_name
                    for analysis_name, url in calls_to_make
                }

                for future in future_to_type:
                    analysis_name = future_to_type[future]
                    try:
                        result = future.result(timeout=self.TIMEOUT)
                        if result["success"]:
                            results[f"{analysis_name}_analysis"] = result["data"]
                        else:
                            errors[f"{analysis_name}_error"] = result["error"]
                    except Exception as e:
                        logger.error(f"Error in {analysis_name} analysis: {e}")
                        errors[f"{analysis_name}_error"] = str(e)

            response_data = {"text": text}

            if 'hate_speech_analysis' in results:
                hate_data = results['hate_speech_analysis']
                response_data['hate_speech_analysis'] = {
                    "is_hate_speech": hate_data.get("is_hate_speech"),
                    "confidence": hate_data.get("confidence"),
                    "category": hate_data.get("category"),
                    "severity": hate_data.get("severity"),
                    "detected_keywords": hate_data.get("detected_keywords", []),
                    "explanation": hate_data.get("explanation")
                }

            if 'misinformation_analysis' in results:
                misinfo_data = results['misinformation_analysis']
                response_data['misinformation_analysis'] = {
                    "label": misinfo_data.get("label"),
                    "confidence": misinfo_data.get("confidence"),
                    "severity": misinfo_data.get("severity"),
                    "explanation": misinfo_data.get("explanation")
                }

            if errors:
                response_data['errors'] = errors

            if results:
                first_result = list(results.values())[0]
                response_data['timestamp'] = first_result.get('timestamp')

            if results and not errors:
                return Response(response_data, status=status.HTTP_200_OK)
            elif results and errors:
                return Response(response_data, status=status.HTTP_206_PARTIAL_CONTENT)
            else:
                return Response(
                    {
                        "text": text,
                        "errors": errors,
                        "message": "All analysis services failed"
                    },
                    status=status.HTTP_502_BAD_GATEWAY
                )

        except requests.exceptions.Timeout:
            logger.error("Timeout error when calling analysis models")
            return Response(
                {"error": "Analysis services are taking too long to respond. Please try again."},
                status=status.HTTP_408_REQUEST_TIMEOUT
            )

        except Exception as e:
            logger.error(f"Unexpected error in unified analysis: {e}")
            return Response(
                {"error": "An unexpected error occurred. Please try again."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )