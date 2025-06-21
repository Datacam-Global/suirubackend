from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db.models import Avg
from monitoring.models import FacebookPost, Alert, ContentModelAnalysis, PlatformAnalytics

class DashboardKPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        total_content = FacebookPost.objects.count()
        active_threats = Alert.objects.filter(status__in=['new', 'in_progress']).count()
        accuracy_qs = ContentModelAnalysis.objects.exclude(confidence=None)
        accuracy = round(accuracy_qs.aggregate(Avg('confidence'))['confidence__avg'] or 0, 2)
        platforms = PlatformAnalytics.objects.values('platform_name').distinct().count()
        last_post = FacebookPost.objects.order_by('-updated_at').first()
        last_alert = Alert.objects.order_by('-updated_at').first()
        last_update = None
        if last_post and last_alert:
            last_update = max(last_post.updated_at, last_alert.updated_at)
        elif last_post:
            last_update = last_post.updated_at
        elif last_alert:
            last_update = last_alert.updated_at
        else:
            last_update = timezone.now()
        return Response({
            "totalContent": total_content,
            "activeThreats": active_threats,
            "accuracy": accuracy,
            "platforms": platforms,
            "lastUpdate": last_update.isoformat()
        })
