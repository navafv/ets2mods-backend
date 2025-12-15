from rest_framework import serializers
from .models import Review, ReviewReport

class ReviewSerializer(serializers.ModelSerializer):
    user_username = serializers.ReadOnlyField(source='user.username')
    user_avatar = serializers.ReadOnlyField(source='user.avatar.url')
    helpful_count = serializers.IntegerField(source='helpful_votes.count', read_only=True)
    is_helpful = serializers.SerializerMethodField()
    is_owner = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = ['id', 'user_username', 'user_avatar', 'rating', 'content', 'created_at', 'helpful_count', 'is_helpful', 'is_owner']
        read_only_fields = ['rating', 'content'] # Assume update logic handled separately or basic CRUD

    def get_is_helpful(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.helpful_votes.filter(id=request.user.id).exists()
        return False

    def get_is_owner(self, obj):
        request = self.context.get('request')
        return request and request.user == obj.user

class ReviewCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['mod', 'rating', 'content']
    
    def validate(self, data):
        # Additional check for uniqueness at serializer level
        user = self.context['request'].user
        if Review.objects.filter(user=user, mod=data['mod']).exists():
            raise serializers.ValidationError("You have already reviewed this mod.")
        return data