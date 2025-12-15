from rest_framework import viewsets, permissions, status, decorators
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Review, ReviewReport
from .serializers import ReviewSerializer, ReviewCreateSerializer

class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        # Filter by specific mod if provided in query params
        mod_id = self.request.query_params.get('mod_id')
        if mod_id:
            return Review.objects.filter(mod_id=mod_id)
        return Review.objects.all()

    def get_serializer_class(self):
        if self.action == 'create':
            return ReviewCreateSerializer
        return ReviewSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    # 3. Helpful Votes
    @decorators.action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def vote(self, request, pk=None):
        review = self.get_object()
        if review.helpful_votes.filter(id=request.user.id).exists():
            review.helpful_votes.remove(request.user)
            return Response({'status': 'removed'})
        else:
            review.helpful_votes.add(request.user)
            return Response({'status': 'added'})

    # 4. Report Review
    @decorators.action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def report(self, request, pk=None):
        review = self.get_object()
        reason = request.data.get('reason', 'spam')
        ReviewReport.objects.create(reporter=request.user, review=review, reason=reason)
        return Response({'status': 'reported'})