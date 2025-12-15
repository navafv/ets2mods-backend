from django.contrib import admin
from .models import Mod, ModImage, GameVersion, DLC, Collection, Report

class ModImageInline(admin.TabularInline):
    model = ModImage
    extra = 1

@admin.register(Mod)
class ModAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'author', 'status', 'download_count', 'average_rating')
    list_filter = ('status', 'category', 'game_versions', 'created_at')
    search_fields = ('title', 'description', 'author__username')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [ModImageInline]
    filter_horizontal = ('game_versions', 'required_dlcs')
    actions = ['approve_mods', 'reject_mods']

    def approve_mods(self, request, queryset):
        queryset.update(status='published')
    
    def reject_mods(self, request, queryset):
        queryset.update(status='rejected')

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('mod', 'reason', 'reporter', 'resolved', 'created_at')
    list_filter = ('resolved', 'reason')
    actions = ['mark_resolved']

    def mark_resolved(self, request, queryset):
        queryset.update(resolved=True)

admin.site.register(GameVersion)
admin.site.register(DLC)
admin.site.register(Collection)