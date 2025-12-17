from django.db import models

class Tutorial(models.Model):
    title = models.CharField(max_length=200)
    video_url = models.URLField(help_text="YouTube embed URL")
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title