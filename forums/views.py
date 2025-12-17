from rest_framework import viewsets, permissions, decorators, status
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from django.db.models import F
from .models import Thread, ForumPost, Notification
from .serializers import ThreadListSerializer, ForumPostSerializer

class ThreadViewSet(viewsets.ModelViewSet):
    queryset = Thread.objects.all().order_by('-is_pinned', '-created_at')
    serializer_class = ThreadListSerializer
    lookup_field = 'slug'

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        Thread.objects.filter(pk=instance.pk).update(view_count=F('view_count') + 1)
        instance.refresh_from_db()
        return super().retrieve(request, *args, **kwargs)

class PostViewSet(viewsets.ModelViewSet):
    serializer_class = ForumPostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        queryset = ForumPost.objects.all()
        thread_slug = self.kwargs.get('thread_slug') or self.request.query_params.get('thread_slug')
        if thread_slug:
            return queryset.filter(thread__slug=thread_slug)
        return queryset

    def perform_create(self, serializer):
        thread_id = self.request.data.get('thread_id')
        
        if not thread_id:
            raise ValidationError({"thread_id": "This field is required."})

        # Save the post
        post = serializer.save(author=self.request.user, thread_id=thread_id)
        
        # Send notification to parent author if this is a reply
        if post.parent and post.parent.author != self.request.user:
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
            action = 'removed'
        else:
            post.likes.add(request.user)
            action = 'added'
        return Response({'status': action})