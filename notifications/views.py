from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from notifications.models import Notification
from rest_framework.response import Response

class NotiicationListView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request) :
        notifications = Notification.objects.filter(recipient=request.user)
        unread_count = notifications.filter(is_read = False).count()
        recent = notifications[:30]

        
        return Response({
            "unread_count": unread_count,
            "results": [
                {
                    "id": n.id,
                    "kind": n.kind,
                    "message": n.message,
                    "is_read": n.is_read,
                    "created_at": n.created_at,
                }
                for n in recent
            ],
        })


class NotificationMarkReadView(APIView) :
    permission_classes = [IsAuthenticated]

    def post(self, request):
        qs = Notification.objects.filter(recipient=request.user, is_read=False)
        if not request.data.get('all'):
            qs = qs.filter(id__in=request.data.get('ids', []))
        qs.update(is_read=True)
        return Response(status=204)