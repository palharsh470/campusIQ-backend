from django.shortcuts import render
from rest_framework.views import APIView
from users.permissions import IsTeacher
from rest_framework.response import Response
from classes.models import ClassGroup, TeacherAssignment
from django.core.mail import EmailMessage
from smtplib import SMTPException
import logging
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

        student_emails = list(
            class_group.enrollments.select_related("student").values_list("student__email", flat = True)
        )


        if not student_emails:
            return Response({"detail": "No students enrolled in this class yet."}, status=400)

        try:
            email = EmailMessage(
                subject=subject,
                body=message,
                to=[],
                bcc=student_emails,
            )
            email.send(fail_silently=False)
        except SMTPException:
            logger.exception("Announcement email send failed")
            return Response(
                {"detail": "Couldn't send the announcement right now. Please try again."},
                status=502,
            )

        Announcement.objects.create(
            teacher=request.user,
            class_group=class_group,
            subject=subject,
            message=message,
            recipient_count=len(student_emails),
        )

        return Response({"sent_to": len(student_emails)}, status=status.HTTP_201_CREATED)