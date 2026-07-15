from django.db import models
from django.contrib.auth.models import User
from django_cryptography.fields import encrypt


class StudentProfile(models.Model):
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='student_profile',
        verbose_name="User"
    )
    college_name = models.CharField(
        max_length=255, 
        blank=True, 
        null=True, 
        verbose_name="College Name"
    )
    branch = models.CharField(
        max_length=255, 
        blank=True, 
        null=True, 
        verbose_name="Branch"
    )
    year = models.IntegerField(
        blank=True, 
        null=True, 
        verbose_name="Year of Study"
    )
    gemini_api_key = encrypt(
    models.CharField(
        max_length=255,
        blank=True,
        null=True
    )
    )
    career_goal = models.TextField(
        blank=True, 
        null=True, 
        verbose_name="Career Goal"
    )
    github = models.URLField(
        max_length=255, 
        blank=True, 
        null=True, 
        verbose_name="GitHub Profile"
    )
    linkedin = models.URLField(
        max_length=255, 
        blank=True, 
        null=True, 
        verbose_name="LinkedIn Profile"
    )
    portfolio = models.URLField(
        max_length=255, 
        blank=True, 
        null=True, 
        verbose_name="Portfolio URL"
    )
    created_at = models.DateTimeField(
        auto_now_add=True, 
        verbose_name="Created At"
    )
    updated_at = models.DateTimeField(
        auto_now=True, 
        verbose_name="Updated At"
    )

    class Meta:
        verbose_name = "Student Profile"
        verbose_name_plural = "Student Profiles"
        ordering = ['-created_at']

    def __str__(self):
        college = self.college_name if self.college_name else "Unspecified College"
        branch = self.branch if self.branch else "Unspecified Branch"
        return f"Profile of {self.user.username} | {college} ({branch})"


class Skill(models.Model):
    student = models.ForeignKey(
        StudentProfile, 
        on_delete=models.CASCADE, 
        related_name='skills',
        verbose_name="Student"
    )
    skill_name = models.CharField(
        max_length=100, 
        verbose_name="Skill Name"
    )
    skill_level = models.CharField(
        max_length=50, 
        verbose_name="Skill Level"
    )

    class Meta:
        verbose_name = "Skill"
        verbose_name_plural = "Skills"
        ordering = ['student', 'skill_name']

    def __str__(self):
        return f"Skill: {self.skill_name} ({self.skill_level}) for {self.student.user.username}"


class Resume(models.Model):
    student = models.ForeignKey(
        StudentProfile, 
        on_delete=models.CASCADE, 
        related_name='resumes',
        verbose_name="Student"
    )
    resume_file = models.FileField(
        upload_to='resumes/', 
        verbose_name="Resume File"
    )
    job_description = models.TextField(
    blank=True,
    null=True,
    verbose_name="Job Description"
    )
    resume_text = models.TextField(
        blank=True, 
        null=True, 
        verbose_name="Resume Text Content"
    )
    analysis_status = models.CharField(
        max_length=20,
        default="Uploaded"
    )
    uploaded_at = models.DateTimeField(
        auto_now_add=True, 
        verbose_name="Uploaded At"
    )

    class Meta:
        verbose_name = "Resume"
        verbose_name_plural = "Resumes"
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"Resume of {self.student.user.username} (Uploaded {self.uploaded_at.strftime('%Y-%m-%d %H:%M')})"
