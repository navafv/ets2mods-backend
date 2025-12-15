import django_filters
from django.db.models import Q
from .models import Mod

class ModFilter(django_filters.FilterSet):
    min_rating = django_filters.NumberFilter(field_name='average_rating', lookup_expr='gte')
    category = django_filters.CharFilter(field_name='category__slug')
    game_version = django_filters.CharFilter(field_name='game_versions__version')
    author = django_filters.CharFilter(field_name='author__username')
    
    # Custom search to handle full-text search better than standard DRF
    q = django_filters.CharFilter(method='filter_search')

    class Meta:
        model = Mod
        fields = ['category', 'game_version', 'status', 'author']

    def filter_search(self, queryset, name, value):
        from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
        
        # Postgres Full-Text Search
        vector = SearchVector('title', weight='A') + \
                 SearchVector('description', weight='B') + \
                 SearchVector('author__username', weight='C')
        
        query = SearchQuery(value)
        
        return queryset.annotate(
            rank=SearchRank(vector, query)
        ).filter(rank__gte=0.1).order_by('-rank')