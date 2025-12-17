from datetime import timezone
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
from django.db import connection
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

# Simple Health Check
def health_check(request):
    try:
        connection.ensure_connection()
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    return JsonResponse({
        "status": "ok",
        "database": db_status,
        "timestamp": timezone.now().isoformat(),
    })

# Swagger Schema
schema_view = get_schema_view(
   openapi.Info(
      title="ETS2 Mods API",
      default_version='v1',
      description="API documentation for ETS2 Mods Platform",
      contact=openapi.Contact(email="contact@ets2mods.com"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('health/', health_check, name='health_check'),

    # Documentation
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    
    # Auth
    path('api/auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('accounts/', include('allauth.urls')),

    # Apps
    path('api/', include([
        path('users/', include('users.urls')),
        path('mods/', include('mods.urls')),
        path('categories/', include('categories.urls')),
        path('reviews/', include('reviews.urls')),
        path('forums/', include('forums.urls')),
        path('analytics/', include('analytics.urls')),
    ])),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)