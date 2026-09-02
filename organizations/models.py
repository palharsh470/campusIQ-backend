from django.db import models

class Organization(models.Model):
    class OrgType(models.TextChoices):
        college = "COLLEGE", "college"

    name = models.CharField(max_length=255)
    type = models.CharField(max_length=20, choices=OrgType.choices)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name