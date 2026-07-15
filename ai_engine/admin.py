from django.contrib import admin
from .models import AIAnalysis

@admin.register(AIAnalysis)
class AIAnalysisAdmin(admin.ModelAdmin):
    list_display = ('resume', 'overall_score', 'technical_score', 'ats_score', 'analysis_date')
    search_fields = ('student__user__username', 'resume_quality', 'career_domain')
    list_filter = ('overall_score', 'ats_score', 'analysis_date')
    readonly_fields = ('analysis_date',)
