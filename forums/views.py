from rest_framework import viewsets, permissions, decorators
from rest_framework.response import Response
from .models import Thread, ForumPost, Notification
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
        # Check query params instead: /api/forums/posts/?thread_slug=xyz
        queryset = ForumPost.objects.all()
        thread_slug = self.kwargs.get('thread_slug') or self.request.query_params.get('thread_slug')
        
        if thread_slug:
            return queryset.filter(thread__slug=thread_slug)
        return queryset

    def perform_create(self, serializer):
        # Ensure thread_id is passed in body
        thread_id = self.request.data.get('thread_id')
        post = serializer.save(author=self.request.user, thread_id=thread_id)
        
        # Create Notification if replying
        if post.parent:
            Notification.objects.create(
                recipient=post.parent.author,
                message=f"{self.request.user.username} replied to your comment",
                link=f"/forums/thread/{post.thread.slug}"
            )

    @decorators.action(detail=True, methods=['post'])
    def like(self, request, pk=None):
        post = self.get_object()
        if post.likes.filter(id=request.user.id).exists():
            post.likes.remove(request.user)
        else:
            post.likes.add(request.user)
        return Response({'status': 'ok'})