from django.db import models
from django.conf import settings
from mods.models import Mod

class DownloadLog(models.Model):
    mod = models.ForeignKey(Mod, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    ip_address = models.GenericIPAddressField()
    timestamp = models.DateTimeField(auto_now_add=True)
    user_agent = models.CharField(max_length=255, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['mod', 'ip_address', 'timestamp']),
        ]

    def __str__(self):
        return f"Download of {self.mod.id} by {self.ip_address}"