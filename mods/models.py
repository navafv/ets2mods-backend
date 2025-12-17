from django.db import models
from django.conf import settings
from django.utils.text import slugify
from categories.models import Category
from cloudinary.models import CloudinaryField

class GameVersion(models.Model):
    version = models.CharField(max_length=20, unique=True)
    def __str__(self): return self.version

class DLC(models.Model):
    name = models.CharField(max_length=100)
    def __str__(self): return self.name

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
    slug = models.SlugField(unique=True, max_length=255, blank=True)
    description = models.TextField()
    
    # Versioning
    version = models.CharField(max_length=20, help_text="Mod version (e.g., v1.0)")
    game_versions = models.ManyToManyField(GameVersion, related_name='compatible_mods')
    required_dlcs = models.ManyToManyField(DLC, blank=True, related_name='required_by_mods')

    # Compatibility
    min_game_version = models.CharField(max_length=20, help_text="e.g., 1.48", default="1.0")
    conflicts_with = models.ManyToManyField('self', blank=True, symmetrical=True)
    
    # Files
    file_url = models.URLField(help_text="External download link", blank=True, null=True)
    file_size = models.CharField(max_length=50, help_text="Auto-calculated or manual (e.g., 250 MB)", blank=True)
    file = models.FileField(upload_to='mods/files/', null=True, blank=True)
    
    # Metrics
    download_count = models.PositiveIntegerField(default=0)
    view_count = models.PositiveIntegerField(default=0)
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.0)

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
            models.Index(fields=['download_count']),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.title}-{self.version}")
        
        # Auto-calculate file size if file is present
        # wrapped in try/except because accessing .size on cloud storage 
        # before save completes or if network issues exist can fail.
        if self.file and not self.file_size:
            try:
                size_in_mb = self.file.size / (1024 * 1024)
                self.file_size = f"{size_in_mb:.2f} MB"
            except Exception:
                pass 

        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

class ModImage(models.Model):
    mod = models.ForeignKey(Mod, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='mod_screenshots/')
    is_cover = models.BooleanField(default=False)

class ModScreenshot(models.Model):
    mod = models.ForeignKey(Mod, related_name='screenshots', on_delete=models.CASCADE)
    image = CloudinaryField('image')

class Collection(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    mods = models.ManyToManyField(Mod, related_name='collections')
    is_public = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

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