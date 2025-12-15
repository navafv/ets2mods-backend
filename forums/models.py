from django.db import models
from django.conf import settings
from mptt.models import MPTTModel, TreeForeignKey
from django.utils.text import slugify

class ForumCategory(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    
    class Meta:
        verbose_name_plural = "Forum Categories"

    def __str__(self):
        return self.name

class Thread(models.Model):
    category = models.ForeignKey(ForumCategory, on_delete=models.CASCADE, related_name='threads')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    content = models.TextField()
    
    # Status
    is_pinned = models.BooleanField(default=False)
    is_locked = models.BooleanField(default=False)
    
    # Activity
    view_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

class ForumPost(MPTTModel):
    thread = models.ForeignKey(Thread, on_delete=models.CASCADE, related_name='posts')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    
    # MPTT Fields
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    
    likes = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='liked_posts', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class MPTTMeta:
        order_insertion_by = ['created_at']

# Simple Notification System
class Notification(models.Model):
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    message = models.CharField(max_length=255)
    link = models.CharField(max_length=255) # Frontend route (e.g., /forums/thread/1)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)