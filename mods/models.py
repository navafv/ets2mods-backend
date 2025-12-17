from django.db import models
from django.utils.text import slugify
from categories.models import Category
import uuid

class Mod(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending Approval'),
        ('published', 'Published'),
        # Rejected mods are simply deleted to save space
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True, max_length=255)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='mods')
    
    # Content
    description = models.TextField()
    uploader_name = models.CharField(max_length=100, default="Anonymous", help_text="Name displayed as the uploader")
    # Added fields for tracking
    uploader_email = models.EmailField(blank=True, null=True, help_text="Private email for contact/tracking")
    uploader_ip = models.GenericIPAddressField(blank=True, null=True, help_text="Uploader's IP address")
    
    youtube_url = models.URLField(blank=True, null=True, help_text="Embed link for video preview")
    
    # Meta
    version = models.CharField(max_length=50, blank=True, help_text="e.g. 1.0")
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Counters (Simple implementation)
    view_count = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            # 1. Generate the base slug
            base_slug = slugify(self.title)
            
            # 2. Handle cases where slugify returns empty (e.g., non-English titles)
            if not base_slug:
                # Fallback to using the UUID or a default string
                base_slug = f"mod-{str(self.id)[:8]}"

            # 3. Ensure Uniqueness (Handle duplicate titles)
            slug = base_slug
            counter = 1
            
            # Keep checking if this slug exists in the DB
            # We exclude the current ID to allow updating the same object without error
            while Mod.objects.filter(slug=slug).exclude(id=self.id).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            
            self.slug = slug
            
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

class DownloadLink(models.Model):
    mod = models.ForeignKey(Mod, related_name='download_links', on_delete=models.CASCADE)
    name = models.CharField(max_length=100, help_text="e.g. ShareMods, Google Drive")
    url = models.URLField()
    file_size = models.CharField(max_length=50, help_text="e.g. 250 MB")
    
    def __str__(self):
        return f"{self.name} - {self.mod.title}"

class ModImage(models.Model):
    mod = models.ForeignKey(Mod, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='mod_images/')
    is_cover = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        # Ensure only one cover image per mod
        if self.is_cover:
            ModImage.objects.filter(mod=self.mod, is_cover=True).update(is_cover=False)
        super().save(*args, **kwargs)

class Comment(models.Model):
    mod = models.ForeignKey(Mod, related_name='comments', on_delete=models.CASCADE)
    user_name = models.CharField(max_length=100, default="Guest")
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']