from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Auth Endpoints
    path('api/auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('accounts/', include('allauth.urls')),

    # App Endpoints
    path('api/users/', include('users.urls')),
    path('api/mods/', include('mods.urls')),
    path('api/categories/', include('categories.urls')),
    path('api/reviews/', include('reviews.urls')),
    path('api/forums/', include('forums.urls')),
    # path('api/analytics/', include('analytics.urls')),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)