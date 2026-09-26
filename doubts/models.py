from django.db import models
from classes.models import ClassGroup
from lectures.models import Lecture
from django.conf import settings
from skills.models import SkillTag

class Doubt(models.Model):
    class Status(models.TextChoices):
        OPEN = "OPEN", "Open"
        RESOLVED = "RESOLVED", "Resolved"
    class_group = models.ForeignKey(ClassGroup, on_delete=models.CASCADE, related_name="doubts")
    lecture = models.ForeignKey(Lecture, on_delete=models.SET_NULL, null=True , blank=True , related_name="doubts")
    topic = models.ForeignKey(SkillTag, on_delete=models.SET_NULL, null=True, blank=True, related_name="doubts")
    raised_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='doubts_raised')
    title = models.CharField(max_length=255)
    question = models.TextField()
    attachment = models.ImageField(upload_to='doubts/', null=True, blank=True)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.OPEN)
    resolved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='doubts_resolved'
    )
    resolved_at = models.DateTimeField(null=True, blank=True)
    views_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Doubt by {self.raised_by.username} on {self.title} - ({self.status})"

class DoubtMessage(models.Model):
    doubt = models.ForeignKey(Doubt, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='doubt_messages')
    text = models.TextField(blank = True, null = True)
    attachment = models.ImageField(upload_to='doubt_messages/', null=True, blank=True)
    is_accepted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.sender.username}: {self.text[:30]}"


class DoubtLike(models.Model):
    doubt = models.ForeignKey(Doubt, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='doubt_likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('doubt', 'user')


class DoubtMessageLike(models.Model):
    message = models.ForeignKey(DoubtMessage, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='doubt_message_likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('message', 'user')