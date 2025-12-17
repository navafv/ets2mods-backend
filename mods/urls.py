from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ModViewSet, ModImageViewSet, CommentViewSet

router = DefaultRouter()
router.register(r'items', ModViewSet, basename='mod')
router.register(r'images', ModImageViewSet, basename='mod-image')
router.register(r'comments', CommentViewSet, basename='comment')

urlpatterns = [
    path('', include(router.urls)),
]