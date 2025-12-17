from rest_framework import viewsets, serializers
from .models import Tutorial

class TutorialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tutorial
        fields = '__all__'

class TutorialViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tutorial.objects.all().order_by('-created_at')
    serializer_class = TutorialSerializer