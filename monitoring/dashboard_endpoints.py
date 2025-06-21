from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db.models import Avg
from monitoring.models import FacebookPost, Alert, ContentAnalysis, RegisteredPlatform

class DashboardKPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        total_content = FacebookPost.objects.count()
        active_threats = Alert.objects.filter(status__in=['new', 'in_progress']).count()
        # Use ContentAnalysis.confidence_score for accuracy, convert to percentage
        accuracy_qs = ContentAnalysis.objects.exclude(confidence_score=None)
        accuracy = accuracy_qs.aggregate(Avg('confidence_score'))['confidence_score__avg']
        accuracy = round((accuracy or 0) * 100, 2)
        platforms = RegisteredPlatform.objects.count()
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
