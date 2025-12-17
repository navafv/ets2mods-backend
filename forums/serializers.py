from rest_framework import serializers
from .models import ForumCategory, Thread, ForumPost, Notification

class ForumCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ForumCategory
        fields = '__all__'


class ThreadListSerializer(serializers.ModelSerializer):
    author_name = serializers.ReadOnlyField(source='author.username')
    post_count = serializers.IntegerField(source='posts.count', read_only=True)

    class Meta:
        model = Thread
        fields = [
            'id',
            'title',
            'slug',
            'author_name',
            'category',
            'is_pinned',
            'is_locked',
            'view_count',
            'created_at',
            'post_count',
        ]


class ForumPostSerializer(serializers.ModelSerializer):
    author_name = serializers.ReadOnlyField(source='author.username')
    author_avatar = serializers.SerializerMethodField()
    like_count = serializers.IntegerField(source='likes.count', read_only=True)
    is_liked = serializers.SerializerMethodField()

    class Meta:
        model = ForumPost
        fields = [
            'id',
            'content',
            'author_name',
            'author_avatar',
            'created_at',
            'parent',
            'level',
            'like_count',
            'is_liked',
        ]

    def get_author_avatar(self, obj):
        if obj.author.avatar:
            return obj.author.avatar.url
        return None

    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.likes.filter(id=request.user.id).exists()
        return False
