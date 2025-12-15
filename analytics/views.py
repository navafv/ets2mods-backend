from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum, Count
from mods.models import Mod
from .models import DownloadLog

class AnalyticsDashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        # Get user's mods
        user_mods = Mod.objects.filter(author=user)
        
        total_downloads = user_mods.aggregateHb(Sum('download_count'))['download_count__sum'] or 0
        total_mods = user_mods.count()
        
        # Recent downloads (last 10)
        recent_logs = DownloadLog.objects.filter(mod__author=user).order_by('-timestamp')[:10]
        recent_data = [{
            'mod': log.mod.title,
            'ip': log.ip_address,
            'date': log.timestamp
        } for log in recent_logs]

        return Response({
            'total_downloads': total_downloads,
            'total_mods': total_mods,
            'recent_downloads': recent_data
        })