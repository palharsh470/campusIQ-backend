from django.shortcuts import render
from rest_framework import generics, viewsets
from .serializers import ProgramSerializer, ClassGroupSerializer, TeacherAssignmentSerializer, EnrollmentSerializer
from users.permissions import IsDirector
from .models import Program, ClassGroup, Enrollment, TeacherAssignment


class ProgramViewSet(viewsets.ModelViewSet):
    serializer_class = ProgramSerializer
    permission_classes = [IsDirector]

    def get_queryset(self):
        return Program.objects.filter(organization=self.request.user.organization)

    def perform_create(self, serializer):
        serializer.save(organization=self.request.user.organization)

class ClassGroupViewSet(viewsets.ModelViewSet):
    serializer_class = ClassGroupSerializer
    permission_classes = [IsDirector]

    def get_queryset(self):
        return ClassGroup.objects.filter(organization=self.request.user.organization)

    def perform_create(self, serializer):
        serializer.save(organization=self.request.user.organization)

class TeacherAssignmentViewSet(viewsets.ModelViewSet):
    serializer_class = TeacherAssignmentSerializer
    permission_classes = [IsDirector]

    def get_queryset(self):
        return TeacherAssignment.objects.filter(organization=self.request.user.organization)

    def perform_create(self, serializer):
        serializer.save(organization=self.request.user.organization)

class EnrollmentViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = EnrollmentSerializer
    permission_classes = [IsDirector]

    def get_queryset(self):
        qs = Enrollment.objects.filter(class_group__organization=self.request.user.organization)
        class_group_id = self.request.query_params.get('class_group')
        if class_group_id:
            qs = qs.filter(class_group_id=class_group_id)
        return qs