from rest_framework import serializers
from .models import Mod, DownloadLink, ModImage, Comment

class DownloadLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = DownloadLink
        fields = ['id', 'name', 'url', 'file_size']

class ModImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ModImage
        fields = ['id', 'image', 'is_cover']

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['id', 'user_name', 'content', 'created_at']

class ModListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for lists (cover image only)"""
    cover_image = serializers.SerializerMethodField()
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Mod
        fields = ['id', 'title', 'slug', 'uploader_name', 'cover_image', 'category_name', 'created_at', 'view_count']

    def get_cover_image(self, obj):
        cover = obj.images.filter(is_cover=True).first()
        if not cover:
            cover = obj.images.first()
        return cover.image.url if cover else None

class ModDetailSerializer(serializers.ModelSerializer):
    """Full details including all images and links"""
    download_links = DownloadLinkSerializer(many=True, read_only=True)
    images = ModImageSerializer(many=True, read_only=True)
    comments = CommentSerializer(many=True, read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Mod
        fields = '__all__'

class ModCreateSerializer(serializers.ModelSerializer):
    """Serializer for uploading (creating) a mod"""
    # We accept links as a JSON string or list in the request
    download_links = serializers.ListField(
        child=serializers.DictField(), write_only=True
    )
    # Images are usually handled via MultiPartParser separately or separate endpoints, 
    # but to keep it simple, we might upload images after creating the mod ID.
    
    class Meta:
        model = Mod
        fields = ['title', 'description', 'category', 'uploader_name', 'youtube_url', 'version', 'download_links']

    def create(self, validated_data):
        links_data = validated_data.pop('download_links', [])
        mod = Mod.objects.create(status='pending', **validated_data)
        
        for link in links_data:
            DownloadLink.objects.create(mod=mod, **link)
            
        return mod