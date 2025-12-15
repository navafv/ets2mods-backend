from django.contrib import admin
from .models import Mod, ModImage, GameVersion, DLC, Collection, Report

class ModImageInline(admin.TabularInline):
    model = ModImage
    extra = 1

@admin.register(Mod)
class ModAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'author', 'status', 'is_approved', 'created_at')
    list_filter = ('status', 'is_approved', 'category', 'created_at')
    search_fields = ('title', 'description', 'author__username')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [ModImageInline]
    actions = ['approve_mods', 'reject_mods']

    @admin.action(description='Approve selected mods')
    def approve_mods(self, request, queryset):
        queryset.update(status='published', is_approved=True, approved_by=request.user)
    
    @admin.action(description='Reject selected mods')
    def reject_mods(self, request, queryset):
        queryset.update(status='rejected', is_approved=False)

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