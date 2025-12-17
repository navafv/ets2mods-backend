from rest_framework import viewsets, filters, status
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAdminUser
from rest_framework.response import Response
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, F
from django.http import HttpResponseRedirect, Http404

from .models import Mod
from analytics.models import DownloadLog
from .serializers import ModSerializer
from .filters import ModFilter
from .services import check_compatibility
from users.throttles import DownloadRateThrottle

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')

class ModViewSet(viewsets.ModelViewSet):
    serializer_class = ModSerializer
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
        
        # Show approved mods OR mods created by the current user
        if user.is_authenticated:
            return Mod.objects.filter(Q(is_approved=True) | Q(author=user)).distinct()
        
        return Mod.objects.filter(is_approved=True)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        # Atomic update for view count
        Mod.objects.filter(pk=instance.pk).update(view_count=F('view_count') + 1)
        instance.refresh_from_db()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def perform_create(self, serializer):
        serializer.save(
            author=self.request.user,
            status='pending',
            is_approved=False,
        )

    @action(detail=True, methods=['get'], throttle_classes=[DownloadRateThrottle], url_path='download')
    def download(self, request, pk=None):
        mod = self.get_object()
        
        # Check permissions for unapproved mods
        if not mod.is_approved and mod.author != request.user and not request.user.is_staff:
            return Response({'detail': 'Not allowed'}, status=status.HTTP_403_FORBIDDEN)

        # Priority: Direct File -> External URL
        if mod.file:
            # Redirect to the storage URL (Cloudinary/S3) instead of proxying through Django
            return HttpResponseRedirect(mod.file.url)
        
        if mod.file_url:
            return Response({'url': mod.file_url})
            
        raise Http404("File not found")

    @action(detail=True, methods=['post'])
    def track_download(self, request, pk=None):
        mod = self.get_object()
        ip = get_client_ip(request)
        user = request.user if request.user.is_authenticated else None

        # Logic: Log every distinct download event, but you might want to limit 
        # "count" increments to one per IP per day to prevent spam.
        # For now, we log everything but the count increment is atomic.
        
        DownloadLog.objects.create(
            mod=mod,
            ip_address=ip,
            user=user
        )
        
        # Atomic increment
        Mod.objects.filter(pk=mod.pk).update(download_count=F('download_count') + 1)
        
        # Return updated count
        mod.refresh_from_db()
        return Response({'status': 'tracked', 'downloads': mod.download_count})

    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def approve(self, request, pk=None):
        mod = self.get_object()
        mod.is_approved = True
        mod.status = 'published'
        mod.approved_by = request.user
        mod.save()
        return Response({'status': 'approved'})

    @action(detail=False, methods=['get'])
    def suggestions(self, request):
        query = request.query_params.get('q', '')
        if len(query) < 2:
            return Response([])
        results = Mod.objects.filter(title__icontains=query, is_approved=True).values_list('title', flat=True)[:5]
        return Response(results)

    @action(detail=True, methods=['post'], url_path='compatibility-check')
    def compatibility_check(self, request, pk=None):
        mod = self.get_object()
        user_version = request.data.get('game_version', '1.0')
        user_dlcs = request.data.get('dlcs', [])
        installed_mods = request.data.get('installed_mods', [])
        result = check_compatibility(mod, user_version, user_dlcs, installed_mods)
        return Response(result)
    
    @action(detail=False, methods=['get'])
    def search_suggestions(self, request):
        query = request.query_params.get('q', '')
        limit = int(request.query_params.get('limit', 5))
        
        results = Mod.objects.filter(
            Q(title__icontains=query) | 
            Q(description__icontains=query) |
            Q(author__username__icontains=query)
        ).filter(is_approved=True)[:limit]
        
        serializer = self.get_serializer(results, many=True)
        return Response(serializer.data)