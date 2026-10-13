from django.db import models
from django.conf import settings

class Notification(models.Model):
    class Kind(models.TextChoices):
        SUCCESS = "success", "Success"
        ERROR = "error", "Error"

    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    kind = models.CharField(max_length=10, choices=Kind.choices)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']