from django.db import models
from django.conf import settings

class SkillTag(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class SkillReport(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='skill_reports')
    skill = models.ForeignKey(SkillTag, on_delete=models.CASCADE, related_name='reports')
    percentage = models.FloatField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('student', 'skill')
        ordering = ['-percentage']

    def __str__(self):
        return f"{self.student.username} - {self.skill.name}: {self.percentage:.1f}%"