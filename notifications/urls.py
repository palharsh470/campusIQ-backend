from django.urls import path
from .views import NotiicationListView, NotificationMarkReadView

urlpatterns = [
    path("notifications/", NotiicationListView.as_view()),
    path("notifications/mark-read/", NotificationMarkReadView.as_view())
]