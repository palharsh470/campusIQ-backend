from django.db import models
from organizations.models import Organization
from django.conf import settings



class Program(models.Model):
    title = models.CharField(max_length=255)
    organization = models.ForeignKey( Organization, on_delete=models.CASCADE, related_name='programs')
    description = models.TextField()
    duration_weeks = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('title', 'organization')

    def __str__(self):
        return f"{self.title} ({self.organization.name})"


class ClassGroup(models.Model):
    course = models.CharField(max_length=255)
    year = models.IntegerField()
    branch = models.CharField(max_length=255)
    section = models.CharField(max_length=5)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='class_groups')
    current_program = models.ForeignKey(
        Program, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='active_class_groups'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.course} {self.year} {self.branch} {self.section} ({self.current_program.title})"


class TeacherAssignment(models.Model):
    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='teaching_assignments'
    )
    class_group = models.ForeignKey(
        ClassGroup, on_delete=models.CASCADE,
        related_name='teacher_assignments'
    )
    assigned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('teacher', 'class_group')

    def __str__(self):
        return f"{self.teacher.username} -> {self.class_group.course} {self.class_group.year} {self.class_group.branch} {self.class_group.section}"


class Enrollment(models.Model):
    student = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='enrollment'
    )
    class_group = models.ForeignKey(
        ClassGroup, on_delete=models.CASCADE, related_name='enrollments'
    )
    enrolled_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.username} in {self.class_group.course} {self.class_group.year} {self.class_group.branch} {self.class_group.section}"