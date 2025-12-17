from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    pass

class ContactMessage(models.Model):
    SUBJECT_CHOICES = [
        ('inquiry', 'General Inquiry'),
        ('support', 'Support Request'),
        ('dmca', 'DMCA / Copyright'),
        ('feedback', 'Feedback'),
        ('report', 'Report a Mod'),
    ]

    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=50, choices=SUBJECT_CHOICES, default='inquiry')
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_resolved = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} - {self.get_subject_display()}"
    
    class Meta:
        ordering = ['-created_at']