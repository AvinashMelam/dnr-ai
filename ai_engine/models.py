from django.db import models
from students.models import Resume

class AIAnalysis(models.Model):
    
    resume = models.OneToOneField(
        Resume,
        on_delete=models.CASCADE,
        related_name="analysis",
        verbose_name="Resume"
    )
    overall_score = models.IntegerField(
        verbose_name="Overall Score"
    )
    technical_score = models.IntegerField(
        verbose_name="Technical Score"
    )
    resume_quality = models.CharField(
        max_length=100, 
        blank=True, 
        null=True, 
        verbose_name="Resume Quality"
    )
    ats_score = models.IntegerField(
        verbose_name="ATS Score"
    )
    job_match_score = models.IntegerField(
    default=0,
    verbose_name="Job Match Score"
    )
    resume_summary = models.TextField(
        blank=True, 
        null=True, 
        verbose_name="Resume Summary"
    )
    overall_feedback = models.TextField(
    blank=True,
    null=True,
    verbose_name="Overall Feedback"
    )

    strengths = models.TextField(
        blank=True, 
        null=True, 
        verbose_name="Strengths"
    )
    weaknesses = models.TextField(
        blank=True, 
        null=True, 
        verbose_name="Weaknesses"
    )
    found_skills = models.TextField(
    blank=True,
    null=True,
    verbose_name="Found Skills"
    )
    missing_skills = models.TextField(
        blank=True, 
        null=True, 
        verbose_name="Missing Skills"
    )
    learning_priority = models.TextField(
        blank=True, 
        null=True, 
        verbose_name="Learning Priority"
    )
    improvement_tips = models.TextField(
    blank=True,
    null=True,
    verbose_name="Improvement Tips"
    )
    job_roles = models.TextField(
        blank=True, 
        null=True, 
        verbose_name="Job Roles"
    )
    interview_readiness_score = models.IntegerField(
        default=0,
        verbose_name="Interview Readiness Score"
    )
    analysis_date = models.DateTimeField(
        auto_now_add=True, 
        verbose_name="Analysis Date"
    )

    class Meta:
        verbose_name = "AI Analysis"
        verbose_name_plural = "AI Analyses"
        ordering = ['-analysis_date']

    def __str__(self):
        return f"{self.resume.student.user.username} | Overall: {self.overall_score} | ATS: {self.ats_score}"