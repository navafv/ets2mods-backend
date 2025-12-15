from rest_framework import viewsets, filters, status, decorators
from rest_framework.response import Response
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from .models import Mod
from .serializers import ModSerializer
from .filters import ModFilter

class ModViewSet(viewsets.ModelViewSet):
    serializer_class = ModSerializer
    queryset = Mod.objects.filter(is_approved=True)
    
    # Configuration
    filterset_class = ModFilter
    ordering_fields = ['created_at', 'total_downloads', 'average_rating']
    ordering = ['-created_at'] # Default sort
    
    # 4. Search & Filter
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'game_versions', 'author']
    search_fields = ['title', 'description']

    def get_queryset(self):
        # Admin sees all, Regular users see only approved or their own
        user = self.request.user
        if user.is_staff:
            return Mod.objects.all()
        return Mod.objects.filter(is_approved=True) | Mod.objects.filter(author=user)

    # 5. Download Analytics Endpoint
    @decorators.action(detail=True, methods=['post'])
    def track_download(self, request, pk=None):
        mod = self.get_object()
        # Prevent duplicate counts from same IP (simple logic)
        ip = request.META.get('REMOTE_ADDR')
        if not DownloadLog.objects.filter(mod=mod, ip_address=ip).exists():
            mod.total_downloads += 1
            mod.save()
            DownloadLog.objects.create(mod=mod, ip_address=ip, user=request.user if request.user.is_authenticated else None)
        return Response({'status': 'tracked'})

    # 7. Mod Approval Workflow (Admin Only)
    @decorators.action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def approve(self, request, pk=None):
        mod = self.get_object()
        mod.is_approved = True
        mod.approved_by = request.user
        mod.save()
        return Response({'status': 'approved'})

    # 8. Bulk Operations (Admin Only)
    @decorators.action(detail=False, methods=['post'], url_path='bulk-delete', permission_classes=[IsAdminUser])
    def bulk_delete(self, request):
        ids = request.data.get('ids', [])
        Mod.objects.filter(id__in=ids).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @decorators.action(detail=False, methods=['get'])
    def suggestions(self, request):
        query = request.query_params.get('q', '')
        if len(query) < 2:
            return Response([])
            
        # Fast query for suggestions (limit 5)
        results = Mod.objects.filter(
            title__icontains=query, 
            is_approved=True
        ).values_list('title', flat=True)[:5]
        
        return Response(results)
    
    @action(detail=True, methods=['post'], url_path='compatibility-check')
    def check_compatibility(self, request, pk=None):
        mod = self.get_object()
        
        # Get user data from request body
        user_version = request.data.get('game_version', '1.0')
        user_dlcs = request.data.get('dlcs', []) # List of DLC IDs
        installed_mods = request.data.get('installed_mods', []) # List of Mod IDs

        result = check_compatibility(mod, user_version, user_dlcs, installed_mods)
        
        return Response(result)