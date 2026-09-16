from django.shortcuts import render
from rest_framework import viewsets
from .serializers import ProgramSerializer, ClassGroupSerializer, TeacherAssignmentSerializer, EnrollmentSerializer
from users.permissions import IsDirector, IsStudent, IsTeacher
from rest_framework import permissions
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

    def get_queryset(self):
        user = self.request.user
        if user.role == "DIRECTOR" :
            return ClassGroup.objects.filter(organization=user.organization)
        if user.role == "TEACHER" :
            return ClassGroup.objects.filter(organization=user.organization, teacher_assignments__teacher=user)
        return None

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"] :
            return [IsDirector()]
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(organization=self.request.user.organization)

class TeacherAssignmentViewSet(viewsets.ModelViewSet):
    serializer_class = TeacherAssignmentSerializer
    permission_classes = [IsDirector]

    def get_queryset(self):
        return TeacherAssignment.objects.filter(teacher__organization=self.request.user.organization)


class EnrollmentViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = EnrollmentSerializer


    def get_queryset(self):
        user = self.request.user
      
        qs = Enrollment.objects.filter(class_group__organization=user.organization)

        if user.role == "STUDENT" :
            qs = qs.filter(student = user)
        elif user.role == "TEACHER" :
            qs = qs.filter(class_group__teacher_assignments__teacher=user)
        class_group_id = self.request.query_params.get('class_group')

        if class_group_id:
            qs = qs.filter(class_group_id=class_group_id)

        
        return qs
    