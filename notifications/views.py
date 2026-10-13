from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from notifications.models import Notification
from rest_framework.response import Response

class NotiicationListView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request) :
        notifications = Notification.objects.filter(recipient=request.user, is_read=False)[:20]
        return Response([
            {"id": n.id, "kind": n.kind, "message": n.message, "created_at": n.created_at}
            for n in notifications
        ])


class NotificationMarkReadView(APIView) :
    permission_classes = [IsAuthenticated]

    def post(self, request):
        ids = request.data.get('ids',[])
        Notification.objects.filter(recipient=request.user, id__in=ids).update(is_read=True)
        return Response(status=204)