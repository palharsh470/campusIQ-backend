from django.shortcuts import render
from rest_framework import generics, viewsets
from .serializers import FeedbackCreateSerializer, FeedbackListSerializer
from users.permissions import IsStudent, IsDirector
from .models import Feedback
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from classes.models import Enrollment
from rest_framework.exceptions import NotFound

class SubmitFeedbackView(generics.CreateAPIView):
    serializer_class = FeedbackCreateSerializer
    permission_classes = [IsStudent]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"detail": "Feedback submitted successfully."}, status=status.HTTP_201_CREATED)

class FeedbackViewSet(viewsets.ModelViewSet):
    serializer_class = [FeedbackListSerializer]
    permission_classes = [IsDirector]

    def get_queryset(self):
        
        qs = Feedback.objects.filter(
            class_group__organization=self.request.user.organization
        ).select_related('teacher', 'class_group', 'program')

        teacher_id = self.request.query_params.get('teacher')
        if teacher_id:
            qs = qs.filter(teacher_id=teacher_id)
        return qs


class LastFeedbackDateView(APIView):
    permission_classes = [IsStudent]

    def get(self, request):
        enrollment_id = request.query_params.get('enrollment')
        if not enrollment_id:
            return Response({"detail": "enrollment query param is required."}, status=400)

        try:
           
            enrollment = Enrollment.objects.select_related(
                'class_group', 'class_group__current_program'
            ).get(id=enrollment_id, student=request.user)
        except Enrollment.DoesNotExist:
            raise NotFound("Enrollment not found.")

        class_group = enrollment.class_group
        student = enrollment.student
        teacher = class_group.teacher_assignments.first().teacher if class_group.teacher_assignments.exists() else None
        program = class_group.current_program

        if not teacher or not program:
            return Response(
                {"detail": "This class group has no assigned teacher or program."},
                status=400,
            )

        feedback = Feedback.objects.filter(
            class_group=class_group,
            teacher=teacher,
            student=student,
            program=program,
        ).order_by('-created_at').first()

        return Response({
            "available": feedback is not None,
            "feedback_date": feedback.created_at if feedback else None,
        })