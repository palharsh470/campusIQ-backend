from django.db import models
from lectures.models import Lecture
from classes.models import ClassGroup, Program
from django.conf import settings

class Assignment(models.Model):
    lecture = models.ForeignKey(Lecture, on_delete= models.CASCADE, related_name="assignments" )
    title = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} ({self.lecture.title})"


class AssignmentQuestion(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return self.text[:50]

class AssignmentOption(models.Model):
    question = models.ForeignKey(AssignmentQuestion, on_delete=models.CASCADE, related_name='options')
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.text

class AssignmentSubmission(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='assignment_submissions')
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='submissions')
    score_percentage = models.FloatField(default=0)
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-submitted_at']  

    def __str__(self):
        return f"{self.student.username} - {self.assignment.title} ({self.score_percentage:.0f}%)"

class AssignmentAnswer(models.Model):
    submission = models.ForeignKey(AssignmentSubmission, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(AssignmentQuestion, on_delete=models.CASCADE, related_name='answers')
    selected_option = models.ForeignKey(AssignmentOption, on_delete=models.SET_NULL, null=True, related_name='answers')

    class Meta:
        unique_together = ('submission', 'question')

    def __str__(self):
        return f"Q{self.question_id} -> {self.selected_option_id}"


class Quiz(models.Model):
    class_group = models.ForeignKey(ClassGroup, on_delete=models.CASCADE, related_name='quizzes')
    program = models.ForeignKey(Program, on_delete=models.CASCADE, related_name='quizzes')
    title = models.CharField(max_length=255)
    covers_up_to_day = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['covers_up_to_day']

    def __str__(self):
        return f"{self.title} (up to Day {self.covers_up_to_day})"

class QuizQuestion(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return self.text[:50]


class QuizOption(models.Model):
    question = models.ForeignKey(QuizQuestion, on_delete=models.CASCADE, related_name='options')
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.text


class QuizSubmission(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='quiz_submissions')
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='submissions')
    score_percentage = models.FloatField(default=0)
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'quiz')  
        ordering = ['-submitted_at']

    def __str__(self):
        return f"{self.student.username} - {self.quiz.title} ({self.score_percentage:.0f}%)"

class QuizAnswer(models.Model):
    submission = models.ForeignKey(QuizSubmission, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(QuizQuestion, on_delete=models.CASCADE, related_name='answers')
    selected_option = models.ForeignKey(QuizOption, on_delete=models.SET_NULL, null=True, related_name='answers')
    is_correct = models.BooleanField(default=False)

    class Meta:
        unique_together = ('submission', 'question')

    def __str__(self):
        return f"Q{self.question_id} -> {self.selected_option_id} ({'correct' if self.is_correct else 'wrong'})"