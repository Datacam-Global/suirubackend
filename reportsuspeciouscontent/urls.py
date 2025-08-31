from django.urls import path
from .views import suspicious_content_report, suspicious_content_report_list, generate_suspicious_content_report, \
    UnifiedAnalysisAPIView

urlpatterns = [
    path('suspecious/', suspicious_content_report, name='suspicious_content_report'),
    path('suspecious/list/', suspicious_content_report_list, name='suspicious_content_report_list'),
    path('reports/analytics/', generate_suspicious_content_report, name='generate_report'),
    path("unified-analyze/", UnifiedAnalysisAPIView.as_view(), name="unified_analyze"),

]
