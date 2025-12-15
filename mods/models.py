from django.db import models
from django.conf import settings
from django.utils.text import slugify
from categories.models import Category
from cloudinary.models import CloudinaryField

class GameVersion(models.Model):
    """e.g., 1.48, 1.49"""
    version = models.CharField(max_length=20, unique=True)
    
    def __str__(self):
        return self.version

class DLC(models.Model):
    """e.g., Iberia, West Balkans"""
    name = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name

class Mod(models.Model):
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('pending', 'Pending Review'),
        ('published', 'Published'),
        ('rejected', 'Rejected'),
    )

    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='mods')
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='mods')
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, max_length=255)
    description = models.TextField()
    
    # Versioning
    version = models.CharField(max_length=20, help_text="Mod version (e.g., v1.0)")
    game_versions = models.ManyToManyField(GameVersion, related_name='compatible_mods')
    required_dlcs = models.ManyToManyField(DLC, blank=True, related_name='required_by_mods')

    # Compatibility Fields (Added default="1.0" to fix migration error)
    min_game_version = models.CharField(max_length=20, help_text="e.g., 1.48", default="1.0")
    conflicts_with = models.ManyToManyField('self', blank=True, symmetrical=True, help_text="Mods known to crash with this one")
    
    # Files (Added null=True, blank=True to make file optional initially)
    file_url = models.URLField(help_text="External download link (S3/Mega/Drive)")
    file_size = models.CharField(max_length=20, help_text="e.g., 250 MB")
    file = models.FileField(upload_to='mods/files/', null=True, blank=True)
    
    # Metrics
    download_count = models.PositiveIntegerField(default=0)
    view_count = models.PositiveIntegerField(default=0)
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.0)

    # Note: Removed 'total_downloads' as it was redundant with 'download_count'
    
    # Approval
    is_approved = models.BooleanField(default=False)
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='approved_mods')
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['average_rating']),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.title}-{self.version}")
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

class ModImage(models.Model):
    mod = models.ForeignKey(Mod, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='mod_screenshots/')
    is_cover = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Image for {self.mod.title}"
    
class ModScreenshot(models.Model):
    mod = models.ForeignKey(Mod, related_name='screenshots', on_delete=models.CASCADE)
    image = CloudinaryField('image')

class Collection(models.Model):
    """User curated playlists (e.g., 'Best Graphics 2025')"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    mods = models.ManyToManyField(Mod, related_name='collections')
    is_public = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
        
class Report(models.Model):
    REASONS = (
        ('spam', 'Spam'),
        ('broken', 'Broken/Outdated'),
        ('stolen', 'Stolen Content'),
        ('inappropriate', 'Inappropriate'),
    )
    reporter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    mod = models.ForeignKey(Mod, on_delete=models.CASCADE, related_name='reports')
    reason = models.CharField(max_length=20, choices=REASONS)
    details = models.TextField()
    resolved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
class ModVersionHistory(models.Model):
    mod = models.ForeignKey(Mod, related_name='versions', on_delete=models.CASCADE)
    version_number = models.CharField(max_length=20)
    changelog = models.TextField()
    file = models.FileField(upload_to='mods/archive/')
    created_at = models.DateTimeField(auto_now_add=True)