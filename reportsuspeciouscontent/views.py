import logging
import random
import uuid
from concurrent.futures.thread import ThreadPoolExecutor
from datetime import datetime, timedelta

import requests
from django.utils import timezone
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status, views, permissions
# Create your views here.
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Count, Avg, Q, F, When, Case, FloatField
from django.db.models.functions import TruncDate
from collections import Counter
import re
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


class DashboardReportsView(APIView):
    """
    Dashboard Report API endpoint matching the specification
    POST /api/dashboard/reports
    """

    @swagger_auto_schema(
        operation_summary="Generate dashboard reports",
        operation_description="Generate dashboard reports for suspicious content within a given date range and filters.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "report_type": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Type of report: daily, weekly, monthly, or custom",
                    default="daily"
                ),
                "date_range": openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "start_date": openapi.Schema(type=openapi.TYPE_STRING, format="date-time"),
                        "end_date": openapi.Schema(type=openapi.TYPE_STRING, format="date-time"),
                    },
                ),
                "filters": openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "platforms": openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Items(type=openapi.TYPE_STRING),
                            description="List of platforms to filter (e.g., facebook, twitter, etc.)"
                        ),
                        "severity_levels": openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Items(type=openapi.TYPE_STRING),
                            description="List of severity levels (low, medium, high, critical)"
                        ),
                        "content_types": openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Items(type=openapi.TYPE_STRING),
                            description="List of content types (hate_speech, misinformation, harassment, spam, fake)"
                        ),
                    },
                ),
            },
            required=["report_type"]
        ),
        responses={
            200: openapi.Response(
                description="Dashboard report generated successfully",
                examples={
                    "application/json": {
                        "success": True,
                        "data": {
                            "report_id": "report_2025_08_31_abcd1234",
                            "generated_at": "2025-08-31T14:23:00Z",
                            "date_range": {"start_date": "2025-08-30T00:00:00Z", "end_date": "2025-08-31T00:00:00Z"},
                            "summary": {"total_posts_analyzed": 120, "hate_speech_count": 25,
                                        "misinformation_count": 18, "harassment_count": 10, "spam_count": 5,
                                        "fake_count": 2}
                        }
                    }
                }
            ),
            400: openapi.Response(description="Bad request / validation error"),
        }
    )
    def post(self, request):
        try:
            # Parse request data
            data = request.data
            report_type = data.get('report_type', 'daily')
            date_range = data.get('date_range', {})
            filters = data.get('filters', {})

            # Parse date range
            start_date = self._parse_date(date_range.get('start_date'))
            end_date = self._parse_date(date_range.get('end_date'))

            # Default date range based on report type
            if not start_date or not end_date:
                start_date, end_date = self._get_default_date_range(report_type)

            # Build base queryset
            queryset = SuspiciousContentReport.objects.filter(
                date_reported__range=[start_date, end_date]
            )

            # Apply filters
            queryset = self._apply_filters(queryset, filters)

            # Generate report data
            report_data = self._generate_report_data(queryset, start_date, end_date)

            return Response({
                "success": True,
                "data": report_data
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                "success": False,
                "error": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

    def _parse_date(self, date_str):
        """Parse ISO 8601 date string"""
        if not date_str:
            return None
        try:
            return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        except:
            return None

    def _get_default_date_range(self, report_type):
        """Get default date range based on report type"""
        end_date = timezone.now()

        if report_type == 'daily':
            start_date = end_date - timedelta(days=1)
        elif report_type == 'weekly':
            start_date = end_date - timedelta(weeks=1)
        elif report_type == 'monthly':
            start_date = end_date - timedelta(days=30)
        else:  # custom
            start_date = end_date - timedelta(days=7)

        return start_date, end_date

    def _apply_filters(self, queryset, filters):
        """Apply filters to queryset"""
        if filters.get('platforms'):
            queryset = queryset.filter(platform__in=filters['platforms'])

        if filters.get('severity_levels'):
            queryset = queryset.filter(urgency_level__in=filters['severity_levels'])

        if filters.get('content_types'):
            # Map API content types to model content types
            content_type_mapping = {
                'hate_speech': 'hatespeech',
                'misinformation': 'misinformation',
                'harassment': 'harassment',
                'spam': 'spam',
                'fake': 'fake'
            }

            model_content_types = []
            for ct in filters['content_types']:
                if ct in content_type_mapping:
                    model_content_types.append(content_type_mapping[ct])

            if model_content_types:
                queryset = queryset.filter(content_type__in=model_content_types)

        return queryset

    def _generate_report_data(self, queryset, start_date, end_date):
        """Generate comprehensive report data from actual database content"""

        # Basic counts
        total_posts = queryset.count()
        hate_speech_count = queryset.filter(content_type='hatespeech').count()
        misinformation_count = queryset.filter(content_type='misinformation').count()
        harassment_count = queryset.filter(content_type='harassment').count()
        spam_count = queryset.filter(content_type='spam').count()
        fake_count = queryset.filter(content_type='fake').count()

        # Average confidence score
        avg_confidence = queryset.aggregate(avg_confidence=Avg('confidence_score'))['avg_confidence'] or 0

        # Platform breakdown - using actual data
        platform_data = []
        platform_stats = queryset.values('platform').annotate(
            total=Count('id'),
            hate_speech=Count('id', filter=Q(content_type='hatespeech')),
            misinformation=Count('id', filter=Q(content_type='misinformation')),
            harassment=Count('id', filter=Q(content_type='harassment')),
            spam=Count('id', filter=Q(content_type='spam')),
            fake=Count('id', filter=Q(content_type='fake'))
        )

        for platform in platform_stats:
            platform_data.append({
                "platform": platform['platform'].title(),
                "total_posts": platform['total'],
                "hate_speech": platform['hate_speech'],
                "misinformation": platform['misinformation'],
                "harassment": platform['harassment'],
                "spam": platform['spam'],
                "fake": platform['fake']
            })

        # Severity distribution
        severity_data = []
        severity_stats = queryset.values('urgency_level').annotate(
            count=Count('id')
        )

        for severity in severity_stats:
            percentage = (severity['count'] / total_posts * 100) if total_posts > 0 else 0
            severity_data.append({
                "severity": severity['urgency_level'],
                "count": severity['count'],
                "percentage": round(percentage, 1)
            })


        top_keywords = self._generate_top_keywords(queryset)


        location_insights = self._generate_location_insights(queryset)


        trends = self._generate_trends_data(queryset, start_date, end_date)

        return {
            "report_id": f"report_{datetime.now().strftime('%Y_%m_%d')}_{str(uuid.uuid4())[:8]}",
            "generated_at": timezone.now().isoformat(),
            "date_range": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            },
            "summary": {
                "total_posts_analyzed": total_posts,
                "hate_speech_count": hate_speech_count,
                "misinformation_count": misinformation_count,
                "harassment_count": harassment_count,
                "spam_count": spam_count,
                "fake_count": fake_count,
                "average_confidence": round(avg_confidence, 2),
                "average_processing_time_ms": 1200  # Fixed value since we don't have this data
            },
            "platform_breakdown": platform_data,
            "severity_distribution": severity_data,
            "top_keywords": top_keywords,
            "location_insights": location_insights,
            "trends": trends
        }

    def _generate_top_keywords(self, queryset):
        """Generate top keywords by analyzing actual content"""
        # Common words to exclude
        stop_words = {'the', 'and', 'is', 'in', 'to', 'of', 'a', 'an', 'on', 'for', 'by', 'with', 'at', 'from'}

        # Extract content from queryset
        contents = queryset.values_list('description', flat=True)

        # Count words across all content
        word_counter = Counter()
        for content in contents:
            if content:
                # Simple word extraction (improve with better NLP if needed)
                words = re.findall(r'\b[a-zA-Z]{3,}\b', content.lower())
                filtered_words = [word for word in words if word not in stop_words]
                word_counter.update(filtered_words)

        # Get top 10 words
        top_words = word_counter.most_common(10)

        # Convert to the required format
        keywords_data = []
        for word, frequency in top_words:
            # Assign severity based on frequency (you can improve this logic)
            if frequency > 100:
                severity = "high"
            elif frequency > 50:
                severity = "medium"
            else:
                severity = "low"

            keywords_data.append({
                "keyword": word.title(),
                "frequency": frequency,
                "severity": severity
            })

        return keywords_data

    def _generate_location_insights(self, queryset):
        """Generate location insights from actual location data"""
        location_insights = []

        # Get location statistics from the database
        location_stats = queryset.exclude(location__isnull=True).exclude(location='').values('location').annotate(
            total_posts=Count('id'),
            hate_speech=Count('id', filter=Q(content_type='hatespeech')),
            misinformation=Count('id', filter=Q(content_type='misinformation')),
            high_severity=Count('id', filter=Q(urgency_level__in=['high', 'critical']))
        )

        # Cameroon locations with risk assessment templates
        cameroon_risk_assessment = {
            "Bamenda": {"risk": "high", "issues": ["Anglophone tensions", "separatist content"]},
            "Buea": {"risk": "high", "issues": ["university tensions", "protest coordination"]},
            "Douala": {"risk": "medium", "issues": ["economic grievances", "corruption claims"]},
            "Yaoundé": {"risk": "medium", "issues": ["political content", "government criticism"]},
            "Garoua": {"risk": "medium", "issues": ["ethnic tensions", "religious conflicts"]},
            "Maroua": {"risk": "high", "issues": ["security concerns", "extremist content"]},
            "Kribi": {"risk": "low", "issues": ["economic disputes", "environmental concerns"]},
            "Bertoua": {"risk": "low", "issues": ["infrastructure complaints", "local politics"]}
        }

        for location in location_stats:
            location_name = location['location']
            total_posts = location['total_posts']

            # Calculate risk level based on actual data
            high_severity_ratio = location['high_severity'] / total_posts if total_posts > 0 else 0

            if high_severity_ratio > 0.3:
                risk_level = "high"
            elif high_severity_ratio > 0.1:
                risk_level = "medium"
            else:
                risk_level = "low"

            # Use template issues or generate based on content
            if location_name in cameroon_risk_assessment:
                common_issues = cameroon_risk_assessment[location_name]["issues"]
            else:
                # Generic issues based on content type distribution
                common_issues = []
                if location['hate_speech'] / total_posts > 0.3:
                    common_issues.append("hate speech content")
                if location['misinformation'] / total_posts > 0.3:
                    common_issues.append("misinformation spread")
                if not common_issues:
                    common_issues = ["various suspicious content"]

            location_insights.append({
                "location": location_name,
                "total_posts": total_posts,
                "risk_level": risk_level,
                "common_issues": common_issues
            })

        return location_insights

    def _generate_trends_data(self, queryset, start_date, end_date):
        """Generate daily trends data from actual database content"""
        trends = []

        # Get daily statistics
        daily_stats = queryset.annotate(date=TruncDate('date_reported')).values('date').annotate(
            total=Count('id'),
            hate_speech=Count('id', filter=Q(content_type='hatespeech')),
            misinformation=Count('id', filter=Q(content_type='misinformation')),
            avg_risk=Avg(
                Case(
                    When(urgency_level='low', then=25),
                    When(urgency_level='medium', then=50),
                    When(urgency_level='high', then=75),
                    When(urgency_level='critical', then=95),
                    default=50,
                    output_field=FloatField()
                )
            )
        ).order_by('date')

        # Convert to the required format
        for day in daily_stats:
            trends.append({
                "date": day['date'].isoformat(),
                "hate_speech_count": day['hate_speech'],
                "misinformation_count": day['misinformation'],
                "average_risk_score": round(day['avg_risk'] or 0, 1)
            })

        return trends

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
