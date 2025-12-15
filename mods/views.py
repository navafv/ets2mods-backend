from rest_framework import viewsets, filters, status, decorators
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAdminUser
from rest_framework.response import Response
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from .models import Mod
from analytics.models import DownloadLog 
from .serializers import ModSerializer
from .filters import ModFilter
from .services import check_compatibility

class ModViewSet(viewsets.ModelViewSet):
    serializer_class = ModSerializer
    queryset = Mod.objects.filter(is_approved=True)
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    filterset_class = ModFilter
    ordering_fields = ['created_at', 'download_count', 'average_rating']
    ordering = ['-created_at']
    
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'game_versions', 'author']
    search_fields = ['title', 'description']

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Mod.objects.all()
        if user.is_authenticated:
            return Mod.objects.filter(is_approved=True) | Mod.objects.filter(author=user)
        return Mod.objects.filter(is_approved=True)

    @action(detail=True, methods=['post'])
    def track_download(self, request, pk=None):
        mod = self.get_object()
        ip = request.META.get('REMOTE_ADDR')
        if not DownloadLog.objects.filter(mod=mod, ip_address=ip).exists():
            mod.download_count += 1
            mod.save()
            user = request.user if request.user.is_authenticated else None
            DownloadLog.objects.create(mod=mod, ip_address=ip, user=user)
        return Response({'status': 'tracked', 'downloads': mod.download_count})

    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def approve(self, request, pk=None):
        mod = self.get_object()
        mod.is_approved = True
        mod.approved_by = request.user
        mod.save()
        return Response({'status': 'approved'})

    @action(detail=False, methods=['post'], url_path='bulk-delete', permission_classes=[IsAdminUser])
    def bulk_delete(self, request):
        ids = request.data.get('ids', [])
        Mod.objects.filter(id__in=ids).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @action(detail=False, methods=['get'])
    def suggestions(self, request):
        query = request.query_params.get('q', '')
        if len(query) < 2:
            return Response([])
        results = Mod.objects.filter(
            title__icontains=query, 
            is_approved=True
        ).values_list('title', flat=True)[:5]
        return Response(results)
    
    @action(detail=True, methods=['post'], url_path='compatibility-check')
    def check_compatibility(self, request, pk=None):
        mod = self.get_object()
        user_version = request.data.get('game_version', '1.0')
        user_dlcs = request.data.get('dlcs', []) 
        installed_mods = request.data.get('installed_mods', []) 
        result = check_compatibility(mod, user_version, user_dlcs, installed_mods)
        return Response(result)