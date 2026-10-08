from django.urls import path
from .views import SendAssignmentView

urlpatterns = [
    path('announcements/send/', SendAssignmentView.as_view(), name='announcement-send')
] 

