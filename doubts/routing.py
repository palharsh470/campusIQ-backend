from django.urls import re_path
from .consumers import DoubtConsumer

websocket_urlpatterns = [
    re_path(r'^ws/doubts/$', DoubtConsumer.as_asgi()),
]