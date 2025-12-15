from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
    class ModderStatus(models.TextChoices):
        REGULAR = 'regular', _('Regular User')
        MODDER = 'modder', _('Modder')
        VERIFIED = 'verified', _('Verified Modder')

    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    bio = models.TextField(max_length=500, blank=True)
    modder_status = models.CharField(
        max_length=20, 
        choices=ModderStatus.choices, 
        default=ModderStatus.REGULAR
    )
    country = models.CharField(max_length=100, blank=True)
    
    # Social links
    website = models.URLField(blank=True)
    discord_handle = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return self.username

class NewsletterSubscription(models.Model):
    email = models.EmailField(unique=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.email