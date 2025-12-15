from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, NewsletterSubscription

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('ETS2 Profile', {'fields': ('modder_status', 'avatar', 'bio', 'country', 'website')}),
    )
    list_display = ('username', 'email', 'modder_status', 'is_staff')
    list_filter = ('modder_status',)

@admin.register(NewsletterSubscription)
class NewsletterAdmin(admin.ModelAdmin):
    list_display = ('email', 'subscribed_at', 'is_active')