from django.db import models
from django.conf import settings
from classes.models import ClassGroup, Program

class Feedback(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="feedback_given")
    teacher = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="feedback_received")
    class_group = models.ForeignKey(ClassGroup, on_delete=models.CASCADE, related_name="feedback")
    program = models.ForeignKey(Program, on_delete=models.CASCADE, related_name='feedback')
    subject_knowledge = models.PositiveSmallIntegerField()
    doubt_resolution = models.PositiveSmallIntegerField()
    teaching_quality = models.PositiveSmallIntegerField()
    practical_learning = models.PositiveSmallIntegerField()
    comments = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Feedback for {self.teacher.username}"
