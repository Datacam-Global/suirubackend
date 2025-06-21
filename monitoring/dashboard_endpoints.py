from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db.models import Avg, Q, Count
from datetime import timedelta
from monitoring.models import FacebookPost, Alert, ContentAnalysis, RegisteredPlatform, ContentModelAnalysis

class DashboardKPIView(APIView):
    """
    API endpoint that returns dashboard KPI metrics for the monitored system.

    Returns:
        JSON object with the following fields:
        - totalContent (int): Total content items monitored (from FacebookPost).
        - activeThreats (int): Number of currently active threats (Alert with status 'new' or 'in_progress').
        - accuracy (float): Detection accuracy as a percentage (average confidence_score from ContentAnalysis).
        - platforms (int): Number of registered platforms (from RegisteredPlatform).
        - lastUpdate (string): ISO timestamp of the most recent update (from FacebookPost or Alert).

    Example:
        {
          "totalContent": 2480000,
          "activeThreats": 23,
          "accuracy": 94.2,
          "platforms": 5,
          "lastUpdate": "2025-06-21T10:00:00Z"
        }
    """
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

class ThreatTrendsView(APIView):
    """
    API endpoint that returns time-series data for threats, misinformation, and hate speech.
    
    Query Parameters:
    - timeframe (string, optional): Range of data (e.g., '24h', '7d', '30d'). Default is '7d'.
    - interval (string, optional): Granularity of data points ('hour' or 'day'). Default is 'day'.
    - platform (string, optional): Filter by platform name (e.g., 'Facebook').
    - region (string, optional): Filter by region (e.g., 'Centre Region').
    
    Example:
        GET /api/dashboard/threat-trends?timeframe=7d&interval=day&platform=Facebook&region=Centre
    
    Response:
        [
          {
            "time": "2025-06-15",
            "threats": 15,
            "misinformation": 8,
            "hate_speech": 7
          },
          ...
        ]
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Parse query params
        timeframe = request.GET.get('timeframe', '7d')
        interval = request.GET.get('interval', 'day')
        platform = request.GET.get('platform')
        region = request.GET.get('region')

        # Determine time range
        now = timezone.now()
        if timeframe.endswith('h'):
            hours = int(timeframe[:-1])
            start_time = now - timedelta(hours=hours)
        else:
            days = int(timeframe[:-1]) if timeframe.endswith('d') else 7
            start_time = now - timedelta(days=days)

        # Choose time format
        if interval == 'hour':
            time_format = '%Y-%m-%dT%H:00:00Z'
            delta = timedelta(hours=1)
        else:
            time_format = '%Y-%m-%d'
            delta = timedelta(days=1)

        # Prepare time buckets
        buckets = []
        t = start_time.replace(minute=0, second=0, microsecond=0)
        while t < now:
            buckets.append(t)
            t += delta

        # Helper for filtering by platform/region
        def alert_filter():
            q = Q(created_at__gte=start_time, created_at__lt=now)
            if platform:
                q &= Q(source__iexact=platform)
            if region:
                q &= Q(location__icontains=region)
            return q
        def analysis_filter(atype):
            q = Q(created_at__gte=start_time, created_at__lt=now, analysis_type=atype)
            if platform:
                q &= Q(post__platform__iexact=platform)
            return q

        # Query all relevant data in range
        alerts = Alert.objects.filter(alert_filter())
        misinfo = ContentModelAnalysis.objects.filter(analysis_filter('misinformation'))
        hate = ContentModelAnalysis.objects.filter(analysis_filter('hate'))

        # Build time-bucketed results
        results = []
        for b in buckets:
            next_b = b + delta
            threats_count = alerts.filter(created_at__gte=b, created_at__lt=next_b).count()
            misinfo_count = misinfo.filter(created_at__gte=b, created_at__lt=next_b).count()
            hate_count = hate.filter(created_at__gte=b, created_at__lt=next_b).count()
            results.append({
                'time': b.strftime(time_format),
                'threats': threats_count,
                'misinformation': misinfo_count,
                'hate_speech': hate_count
            })
        return Response(results)

class PlatformBreakdownView(APIView):
    """
    API endpoint that returns the number of threats detected per social media platform.

    Query Parameters:
    - timeframe (string, optional): Range of data (e.g., '24h', '7d', '30d'). Default is '7d'.
    - region (string, optional): Filter by region (e.g., 'Centre Region').

    Example:
        GET /api/dashboard/platform-breakdown?timeframe=7d&region=Centre

    Response:
        [
          { "name": "Facebook", "threats": 35, "color": "#1877F2" },
          { "name": "X (Twitter)", "threats": 28, "color": "#000000" },
          ...
        ]
    """
    permission_classes = [IsAuthenticated]

    PLATFORM_COLORS = {
        'facebook': '#1877F2',
        'x': '#000000',
        'twitter': '#000000',
        'tiktok': '#FE2C55',
        'instagram': '#E4405F',
        'reddit': '#FF4500',
    }

    def get(self, request):
        from django.utils import timezone
        from datetime import timedelta
        from monitoring.models import Alert, RegisteredPlatform
        timeframe = request.GET.get('timeframe', '7d')
        region = request.GET.get('region')
        now = timezone.now()
        if timeframe.endswith('h'):
            hours = int(timeframe[:-1])
            start_time = now - timedelta(hours=hours)
        else:
            days = int(timeframe[:-1]) if timeframe.endswith('d') else 7
            start_time = now - timedelta(days=days)
        # Get all registered platforms
        platforms = RegisteredPlatform.objects.all()
        results = []
        for platform in platforms:
            q = Alert.objects.filter(source__iexact=platform.name, created_at__gte=start_time, created_at__lt=now)
            if region:
                q = q.filter(location__icontains=region)
            count = q.count()
            color = self.PLATFORM_COLORS.get(platform.name.lower(), None)
            results.append({
                'name': platform.display_name or platform.name,
                'threats': count,
                'color': color
            })
        return Response(results)
