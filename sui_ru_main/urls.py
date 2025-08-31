from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="Sui-Ru MHSMS API",
        default_version='v1',
        description="""
        API documentation for Sui-Ru Monitoring HateSpeech and Misinformation System.
        
        This API provides endpoints for:
        - User Management
        - Alert Management
        - Report Generation
        - Content Analysis
        - Geographic Data
        - Platform Analytics
        - Chat System
        - User Settings
        
        All endpoints require authentication except where specified.
        """,
        terms_of_service="https://www.sui-ru.com/terms/",
        contact=openapi.Contact(email="contact@sui-ru.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
    patterns=[
        path('api/', include('monitoring.urls')),
        path("api/report/", include("reportsuspeciouscontent.urls")),
    ],
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("monitoring.urls")),
    path("api/report/", include("reportsuspeciouscontent.urls")),
    path("api-auth/", include("rest_framework.urls")),
    
    # Swagger URLs
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Serve static files during development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
