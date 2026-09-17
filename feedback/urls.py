from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import SubmitFeedbackView, FeedbackViewSet, LastFeedbackDateView

router = DefaultRouter()
router.register('feedback', FeedbackViewSet, basename='feedback')

urlpatterns = [
    path('feedback/submit/', SubmitFeedbackView.as_view(), name='submit-feedback'),
    path('feedback/last/', LastFeedbackDateView.as_view(), name='last-feedback'),
] + router.urls