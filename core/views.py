from rest_framework import viewsets, mixins
from rest_framework.permissions import AllowAny
from .models import ContactMessage
from .serializers import ContactMessageSerializer

class ContactViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    """
    API endpoint that allows contact messages to be created.
    """
    queryset = ContactMessage.objects.all()
    serializer_class = ContactMessageSerializer
    permission_classes = [AllowAny] # Allow anyone to submit a contact form