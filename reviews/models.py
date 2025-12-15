from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from mods.models import Mod

class Review(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    mod = models.ForeignKey(Mod, on_delete=models.CASCADE, related_name='reviews')
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    content = models.TextField(blank=True)
    
    # Helpful votes
    helpful_votes = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='helpful_reviews', blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'mod') # 1. One review per user per mod
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Recalculate mod average
        reviews = self.mod.reviews.all()
        avg = reviews.aggregate(models.Avg('rating'))['rating__avg']
        self.mod.average_rating = avg if avg else 0
        self.mod.save()

class ReviewReport(models.Model):
    REASONS = (
        ('spam', 'Spam'),
        ('abusive', 'Abusive Language'),
        ('irrelevant', 'Irrelevant'),
    )
    reporter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='reports')
    reason = models.CharField(max_length=20, choices=REASONS)
    resolved = models.BooleanField(default=False)