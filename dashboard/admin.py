from django.contrib import admin
from .models import WorkshopFeedback

@admin.register(WorkshopFeedback)
class WorkshopFeedbackAdmin(admin.ModelAdmin):
    list_display = ('student', 'rating', 'created_at')
    search_fields = ('student__user__username', 'feedback')
    list_filter = ('rating', 'created_at')
    readonly_fields = ('created_at',)
