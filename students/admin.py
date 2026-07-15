from django.contrib import admin
from .models import StudentProfile, Skill, Resume

@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'college_name', 'branch', 'year', 'created_at', 'updated_at')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'college_name', 'branch')
    list_filter = ('year', 'college_name')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ('skill_name', 'skill_level', 'student')
    search_fields = ('skill_name', 'student__user__username')
    list_filter = ('skill_level',)

@admin.register(Resume)
class ResumeAdmin(admin.ModelAdmin):
    list_display = (
        'student',
        'analysis_status',
        'resume_file',
        'uploaded_at'
    )

    search_fields = (
        'student__user__username',
    )

    list_filter = (
        'analysis_status',
        'uploaded_at'
    )

    readonly_fields = (
        'uploaded_at',
    )