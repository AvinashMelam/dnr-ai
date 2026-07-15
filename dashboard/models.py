from django.db import models
from students.models import StudentProfile

class WorkshopFeedback(models.Model):
    student = models.ForeignKey(
        StudentProfile, 
        on_delete=models.PROTECT, 
        related_name='workshop_feedbacks',
        verbose_name="Student"
    )
    rating = models.IntegerField(
        verbose_name="Rating"
    )
    feedback = models.TextField(
        blank=True, 
        null=True, 
        verbose_name="Feedback"
    )
    created_at = models.DateTimeField(
        auto_now_add=True, 
        verbose_name="Created At"
    )

    class Meta:
        verbose_name = "Workshop Feedback"
        verbose_name_plural = "Workshop Feedbacks"
        ordering = ['-created_at']

    def __str__(self):
        return f"Feedback by {self.student.user.username} | Rating: {self.rating} on {self.created_at.strftime('%Y-%m-%d %H:%M')}"
