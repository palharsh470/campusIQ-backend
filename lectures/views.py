from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from .permissions import IsTeacherOrReadOnly
from .models import Lecture, Material
from .serializers import LeactureSerializer, MaterialSerializer
from django.utils import timezone
from .utils import filter_day_locked
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from classes.models import ClassGroup, TeacherAssignment
from rest_framework.exceptions import PermissionDenied
from django.db.models import Count
from .utils import get_current_day


class LecturesViewSet(ModelViewSet):
    serializer_class = LeactureSerializer
    permission_classes = [IsTeacherOrReadOnly]

    def get_queryset(self):
        user = self.request.user
        qs = Lecture.objects.select_related("class_group", "teacher", "program").prefetch_related("materials")
        class_group =  self.request.query_params.get("class_group")
        day_number =  self.request.query_params.get("day")

        if class_group:
           qs = qs.filter(class_group = class_group)
        if day_number:
           qs = qs.filter(day_number = day_number)

        

        if user.role == user.Role.DIRECTOR:
            return qs.filter(class_group__organization=user.organization)
        if user.role == user.Role.TEACHER:
            qs = qs.filter(class_group__teacher_assignments__teacher=user)
            return filter_day_locked(qs, lambda l : l.day_number, lambda l : l.class_group)
        if user.role == user.Role.STUDENT:
            qs = qs.filter(class_group__enrollments__student=user)
            qs = filter_day_locked(qs, lambda l : l.day_number, lambda l : l.class_group)
            return qs
        
        return qs.none()

    def perform_create(self, serializer):
        class_group = serializer.validated_data['class_group']
        serializer.save(teacher=self.request.user, program = class_group.current_program)

    @action(detail=False, methods=['get'], url_path='calendar')
    def calender(self, request):
        class_group_id = request.query_params.get('class_group')

        if not class_group_id:
            return Response({"detail": "class_group is required."}, status=400)

        class_group = get_object_or_404(ClassGroup, pk=class_group_id)
        user = request.user

        if user.role == user.Role.STUDENT:
            enrollment = getattr(user, 'enrollment', None)
            if not enrollment or enrollment.class_group_id != class_group.id:
                raise PermissionDenied("This isn't your class.")
        elif user.role == user.Role.TEACHER:
            if not TeacherAssignment.objects.filter(teacher=user, class_group=class_group).exists():
                raise PermissionDenied("You aren't assigned to this class.")
        elif user.role == user.Role.DIRECTOR:
            if class_group.organization_id != user.organization_id:
                raise PermissionDenied("This class isn't in your organization.")
        else:
            raise PermissionDenied()

        program = class_group.current_program
        if not program or not program.duration_days :
            return Response({"detail": "This class doesn't have a day-wise program set up yet."}, status=400)

        lecture_counts = dict(
            Lecture.objects.filter(class_group = class_group, program = program).
            values('day_number').annotate(count = Count('id')).values_list("day_number", "count")
        )
        applies_lock = user.role in ("TEACHER", "STUDENT")
        started_at = class_group.program_started_at
        max_unlocked_day = None
        if applies_lock and started_at :
            max_unlocked_day = (timezone.now().date() - started_at).days + 1

        days = []
    
        for day in range(1, program.duration_days + 1):
            unlocked = True if not applies_lock else bool(started_at and day <= max_unlocked_day)
            days.append({"day_number": day, "is_unlocked": unlocked, "lecture_count": lecture_counts.get(day, 0)})

        return Response({
            "program_title": program.title,
            "duration_days": program.duration_days,
            "program_started_at": started_at,
            "current_day" : get_current_day(class_group),
            "days": days
        })

class MaterialViewSet(ModelViewSet):
    serializer_class = MaterialSerializer
    permission_classes = [IsTeacherOrReadOnly]


    def get_queryset(self):
        user = self.request.user
        qs = Material.objects.select_related("lecture", "lecture__class_group")

        if user.role == user.Role.DIRECTOR:
            return qs.filter(lecture__class_group__organization=user.organization)
        if user.role == user.Role.TEACHER:
            qs.filter(lecture__class_group__teacher_assignments__teacher=user)
        elif user.role == user.Role.STUDENT:
            qs.filter(lecture__class_group__enrollments__student=user)
        else :
            return qs.none()

        return filter_day_locked(qs, lambda m: m.lecture.day_number, lambda m : m.lecture.class_group)
