from django.shortcuts import render
from users.permissions import IsTeacher
from rest_framework.views import APIView
from rest_framework.response import Response
from lectures.models import Lecture, ClassGroup
from classes.models import TeacherAssignment
from .ai_generation import generate_questions
from rest_framework import status
from rest_framework import viewsets
from .serializers import AssignmentBuilderSerializer, AssignmentTakeSerializer, AssignmentSubmitSerializer
from users.permissions import IsTeacher, IsStudent
from lectures.permissions import IsTeacherOrReadOnly
from lectures.utils import filter_day_locked
from .models import Assignment, AssignmentSubmission, AssignmentAnswer
from rest_framework.decorators import action
from django.db import transaction

class GenerateAssignmentQuestionsView(APIView):
    permission_classes = [IsTeacher]

    def post(self, request):
        lecture_id = request.data.get('lecture')
        num_questions = int(request.data.get('num_questions', 5))

        if not lecture_id:
            return Response({"detail": "lecture is required."}, status=400)
        if not (1 <= num_questions <= 15):
            return Response({"detail": "num_questions must be between 1 and 15."}, status=400)

        lecture = Lecture.objects.filter(pk=lecture_id).select_related('class_group').first()
        if not lecture:
            return Response({"detail": "Lecture not found."}, status=404)

        if not TeacherAssignment.objects.filter(teacher=request.user, class_group=lecture.class_group).exists():
            return Response({"detail": "You are not assigned to this lecture's class."}, status=403)

        content = lecture.title
        if lecture.description:
            content += f"\n\n{lecture.description}"

        try:
            questions = generate_questions(content, num_questions, include_skill=False)
        except Exception:
            return Response(
                {"detail": "Couldn't generate questions right now. Please try again or write them manually."},
                status=502,
            )

        return Response({"questions": questions}, status=status.HTTP_200_OK)

class GenerateQuizQuestionsView(APIView):
    permission_classes = [IsTeacher]

    def post(self, request):
        class_group_id = request.data.get('class_group')
        covers_up_to_day = request.data.get('covers_up_to_day')
        num_questions = int(request.data.get('num_questions', 10))

        if not class_group_id or not covers_up_to_day:
            return Response({"detail": "class_group and covers_up_to_day are required."}, status=400)
        if not (1 <= num_questions <= 20):
            return Response({"detail": "num_questions must be between 1 and 20."}, status=400)

        class_group = ClassGroup.objects.filter(pk=class_group_id).first()
        if not class_group:
            return Response({"detail": "Class group not found."}, status=404)

        if not TeacherAssignment.objects.filter(teacher=request.user, class_group=class_group).exists():
            return Response({"detail": "You are not assigned to this class."}, status=403)

        lectures = Lecture.objects.filter(
            class_group=class_group,
            program=class_group.current_program,
            day_number__lte=covers_up_to_day,
        ).order_by('day_number')

        if not lectures.exists():
            return Response({"detail": "No lectures found in this day range yet."}, status=400)

        content = "\n\n".join(f"Day {l.day_number} — {l.title}\n{l.description}" for l in lectures)

        try:
            questions = generate_questions(content, num_questions, include_skill=True)
        except Exception:
            return Response(
                {"detail": "Couldn't generate questions right now. Please try again or write them manually."},
                status=502,
            )

        return Response({"questions": questions}, status=status.HTTP_200_OK)

class AssignmentViewSet(viewsets.ModelViewSet):
    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return AssignmentBuilderSerializer
        if self.request.user.role == self.request.user.Role.STUDENT:
            return AssignmentTakeSerializer
        return AssignmentBuilderSerializer 
    
    def get_permissions(self):
        if self.action == 'submit':
            return [IsStudent()]
        return [IsTeacherOrReadOnly()]

    def get_queryset(self):
        user = self.request.user
        qs = Assignment.objects.select_related('lecture', 'lecture__class_group').prefetch_related('questions__options')

        if user.role == user.Role.DIRECTOR:
            qs = qs.filter(lecture__class_group__organization=user.organization)
        elif user.role == user.Role.TEACHER:
            qs = qs.filter(lecture__class_group__teacher_assignments__teacher=user)
        elif user.role == user.Role.STUDENT:
            qs = qs.filter(lecture__class_group__enrollments__student=user)
        else:
            return qs.none()

        qs = filter_day_locked(qs, lambda a: a.lecture.day_number, lambda a: a.lecture.class_group)

        lecture_id = self.request.query_params.get('lecture')
        if lecture_id:
            qs = qs.filter(lecture_id=lecture_id)

        return qs

    @action(detail=True, methods=['post'])
    def submit(self, request, pk=None):
        assignment = self.get_object()
        serializer = AssignmentSubmitSerializer(data=request.data, context={'assignment': assignment})
        serializer.is_valid(raise_exception=True)

        answers = serializer.validated_data['answers']
        correct_count = sum(1 for a in answers if a['selected_option'].is_correct)
        score = round((correct_count / len(answers)) * 100, 1)

        with transaction.atomic():
            submission = AssignmentSubmission.objects.create(
                student=request.user, assignment=assignment, score_percentage=score
            )
            AssignmentAnswer.objects.bulk_create([
                AssignmentAnswer(submission=submission, question=a['question'], selected_option=a['selected_option'])
                for a in answers
            ])

        return Response({
            "score_percentage": score,
            "correct_count": correct_count,
            "total_questions": len(answers),
        }, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get'])
    def my_submissions(self, request, pk=None):
        assignment = self.get_object()
        submissions = assignment.submissions.filter(student=request.user).order_by('-submitted_at')
        return Response([
            {"id": s.id, "score_percentage": s.score_percentage, "submitted_at": s.submitted_at}
            for s in submissions
        ])
