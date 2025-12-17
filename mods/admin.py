from django.contrib import admin
from .models import Mod, DownloadLink, ModImage, Comment

class DownloadLinkInline(admin.TabularInline):
    model = DownloadLink
    extra = 1

class ModImageInline(admin.TabularInline):
    model = ModImage
    extra = 1

@admin.register(Mod)
class ModAdmin(admin.ModelAdmin):
    list_display = ('title', 'uploader_name', 'status', 'category', 'created_at')
    list_filter = ('status', 'category')
    search_fields = ('title', 'description')
    inlines = [DownloadLinkInline, ModImageInline]
    actions = ['approve_mods', 'reject_mods']
    prepopulated_fields = {"slug": ("title",)}

    @admin.action(description='Approve selected mods (Publish)')
    def approve_mods(self, request, queryset):
        queryset.update(status='published')

    @admin.action(description='Reject selected mods (Delete)')
    def reject_mods(self, request, queryset):
        # Actually delete them to clear database
        queryset.delete()

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('user_name', 'mod', 'created_at')