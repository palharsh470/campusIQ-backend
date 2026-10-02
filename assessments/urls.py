from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import AssignmentViewSet, GenerateAssignmentQuestionsView, GenerateQuizQuestionsView

router = DefaultRouter()
router.register('assignments', AssignmentViewSet, basename='assignment')

urlpatterns = [
    path('assignments/generate-questions/', GenerateAssignmentQuestionsView.as_view(), name='generate-assignment-questions'),
    path('quizzes/generate-questions/', GenerateQuizQuestionsView.as_view(), name='generate-quiz-questions'),
] + router.urls