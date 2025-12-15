import django_filters
from django.db.models import Q
from .models import Mod

class ModFilter(django_filters.FilterSet):
    min_rating = django_filters.NumberFilter(field_name='average_rating', lookup_expr='gte')
    category = django_filters.CharFilter(field_name='category__slug')
    game_version = django_filters.CharFilter(field_name='game_versions__version')
    author = django_filters.CharFilter(field_name='author__username')
    
    # Custom search
    q = django_filters.CharFilter(method='filter_search')

    class Meta:
        model = Mod
        fields = ['category', 'game_version', 'status', 'author']

    def filter_search(self, queryset, name, value):
        if not value:
            return queryset
        # Standard Django search (Works on SQLite & Postgres)
        return queryset.filter(
            Q(title__icontains=value) | 
            Q(description__icontains=value) |
            Q(author__username__icontains=value)
        )