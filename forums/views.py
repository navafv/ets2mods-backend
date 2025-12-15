from rest_framework import viewsets, permissions, status, decorators
from rest_framework.response import Response
from .models import Thread, ForumPost, Notification, ForumCategory
from .serializers import ThreadListSerializer, ForumPostSerializer, ForumCategorySerializer

class ThreadViewSet(viewsets.ModelViewSet):
    queryset = Thread.objects.all().order_by('-is_pinned', '-created_at')
    serializer_class = ThreadListSerializer
    lookup_field = 'slug'

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        # Increment View Count
        instance.view_count += 1
        instance.save()
        return super().retrieve(request, *args, **kwargs)

class PostViewSet(viewsets.ModelViewSet):
    serializer_class = ForumPostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        return ForumPost.objects.filter(thread__slug=self.kwargs['thread_slug'])

    def perform_create(self, serializer):
        post = serializer.save(author=self.request.user, thread_id=self.request.data.get('thread_id'))
        
        # Create Notification if replying
        if post.parent:
            Notification.objects.create(
                recipient=post.parent.author,
                message=f"{self.request.user.username} replied to your comment",
                link=f"/forums/thread/{post.thread.slug}"
            )

    @decorators.action(detail=True, methods=['post'])
    def like(self, request, pk=None, thread_slug=None):
        post = self.get_object()
        if post.likes.filter(id=request.user.id).exists():
            post.likes.remove(request.user)
        else:
            post.likes.add(request.user)
        return Response({'status': 'ok'})