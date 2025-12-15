from rest_framework import serializers
from .models import Mod, ModScreenshot, ModVersionHistory

class ModScreenshotSerializer(serializers.ModelSerializer):
    image_url = serializers.ReadOnlyField(source='image.url')
    
    class Meta:
        model = ModScreenshot
        fields = ['id', 'image', 'image_url']

class ModSerializer(serializers.ModelSerializer):
    screenshots = ModScreenshotSerializer(many=True, read_only=True)
    uploaded_screenshots = serializers.ListField(
        child=serializers.ImageField(allow_empty_file=False),
        write_only=True, required=False
    )
    
    class Meta:
        model = Mod
        fields = '__all__'
        read_only_fields = ['author', 'download_count', 'is_approved', 'approved_by']

    def create(self, validated_data):
        screenshots_data = validated_data.pop('uploaded_screenshots', [])
        mod = Mod.objects.create(**validated_data)
        
        for image in screenshots_data:
            ModScreenshot.objects.create(mod=mod, image=image)
        return mod