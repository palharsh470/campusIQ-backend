from django.shortcuts import render
from rest_framework.views import APIView
from users.permissions import IsTeacher
from rest_framework.response import Response
from classes.models import ClassGroup, TeacherAssignment
import logging
from .tasks import send_announcement_email
from django.db import transaction
from rest_framework import status
from .models import Announcement

logger = logging.getLogger(__name__)


class SendAssignmentView(APIView) :

    permission_classes = [IsTeacher]

    def post(self, request):
        class_group_id = request.data.get("class_group")
        subject = request.data.get("subject")
        message = request.data.get("message")

        if not all([class_group_id, subject, message]):
            return Response({"detail": "class_group, subject, and message are required."}, status=400)

        class_group = ClassGroup.objects.filter(pk=class_group_id).first()
        if not class_group:
            return Response({"detail": "Class group not found."}, status=404)

        if not TeacherAssignment.objects.filter(teacher=request.user, class_group=class_group).exists():
            return Response({"detail": "You are not assigned to this class."}, status=403)

        if not class_group.enrollments.exists():
             return Response({"detail": "No students enrolled in this class yet."}, status=400)


        announcement =  Announcement.objects.create(
            teacher=request.user,
            class_group=class_group,
            subject=subject,
            message=message,

        )

        transaction.on_commit(lambda: send_announcement_email.delay(announcement.id))

        return Response(
            {"id": announcement.id, "status": announcement.status},
            status=status.HTTP_202_ACCEPTED,
        )