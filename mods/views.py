from rest_framework import viewsets, permissions, status, filters
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.db.models import F
from .models import Mod, ModImage, Comment
from .serializers import (
    ModListSerializer, ModDetailSerializer, ModCreateSerializer, 
    ModImageSerializer, CommentSerializer
)

class ModViewSet(viewsets.ModelViewSet):
    lookup_field = 'slug'
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description', 'uploader_name']
    ordering_fields = ['created_at', 'view_count']

    def get_queryset(self):
        # Admins see everything, Public sees only Published
        if self.request.user.is_staff:
            return Mod.objects.all()
        return Mod.objects.filter(status='published')

    def get_serializer_class(self):
        if self.action == 'list':
            return ModListSerializer
        if self.action == 'create':
            return ModCreateSerializer
        return ModDetailSerializer

    def retrieve(self, request, *args, **kwargs):
        # Increment view count on retrieve
        instance = self.get_object()
        Mod.objects.filter(pk=instance.pk).update(view_count=F('view_count') + 1)
        instance.refresh_from_db()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

class ModImageViewSet(viewsets.ModelViewSet):
    """Separate endpoint to upload images for a specific mod"""
    queryset = ModImage.objects.all()
    serializer_class = ModImageSerializer
    parser_classes = [MultiPartParser, FormParser]

    def create(self, request, *args, **kwargs):
        # Allow creating images linked to a mod ID
        return super().create(request, *args, **kwargs)

class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.AllowAny]

    def perform_create(self, serializer):
        mod_id = self.request.data.get('mod_id')
        if mod_id:
            serializer.save(mod_id=mod_id)