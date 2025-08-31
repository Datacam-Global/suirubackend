from django.urls import path
from .views import suspicious_content_report, suspicious_content_report_list, \
    UnifiedAnalysisAPIView, DashboardReportsView

urlpatterns = [
    path('suspecious/', suspicious_content_report, name='suspicious_content_report'),
    path('suspecious/list/', suspicious_content_report_list, name='suspicious_content_report_list'),
    path('dashboard/reports/', DashboardReportsView.as_view(), name='dashboard-reports'),
    path("unified-analyze/", UnifiedAnalysisAPIView.as_view(), name="unified_analyze"),

]
