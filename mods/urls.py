from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ModViewSet

router = DefaultRouter()
router.register(r'', ModViewSet, basename='mod')

urlpatterns = [
    path('', include(router.urls)),
]