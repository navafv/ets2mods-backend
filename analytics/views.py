from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from django.db.models import Count, Sum
from django.db.models.functions import TruncDate
from mods.models import Mod
from .models import DownloadLog


class AdminAnalyticsView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        # 📊 Downloads per day (last 30 days)
        downloads_per_day = (
            DownloadLog.objects
            .annotate(day=TruncDate('timestamp'))
            .values('day')
            .annotate(count=Count('id'))
            .order_by('day')
        )

        # 📦 Mods per category
        mods_by_category = (
            Mod.objects
            .values('category__name')
            .annotate(count=Count('id'))
            .order_by('-count')
        )

        # 👤 Top authors
        top_authors = (
            Mod.objects
            .values('author__username')
            .annotate(
                mods=Count('id'),
                downloads=Sum('download_count')
            )
            .order_by('-downloads')[:5]
        )

        return Response({
            'downloads_per_day': list(downloads_per_day),
            'mods_by_category': list(mods_by_category),
            'top_authors': list(top_authors),
        })
