from django.urls import path
from .views import suspicious_content_report, suspicious_content_report_list

urlpatterns = [
    path('suspecious/', suspicious_content_report, name='suspicious_content_report'),
    path('suspecious/list/', suspicious_content_report_list, name='suspicious_content_report_list'),
]
