from django.db import models
from classes.models import ClassGroup
from django.conf import settings

class Lecture(models.Model):
    class_group = models.ForeignKey(ClassGroup, on_delete=models.CASCADE, related_name="lectures")
    teacher = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="lectures")
    title = models.CharField(max_length=255)
    url = models.URLField()
    video = models.FileField(upload_to="video/lecture/", blank=True, null=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} ({self.class_group})"

class Material(models.Model):
    lecture = models.ForeignKey(Lecture, on_delete=models.CASCADE, related_name="materials")
    title = models.CharField(max_length=255)
    resource = models.FileField(upload_to="documents/")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.lecture.title}"