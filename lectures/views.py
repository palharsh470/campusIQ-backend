from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from .permissions import IsTeacherOrReadOnly
from .models import Lecture, Material
from .serializers import LeactureSerializer, MaterialSerializer

class LecturesViewSet(ModelViewSet):
    serializer_class = LeactureSerializer
    permission_classes = [IsTeacherOrReadOnly]

    def get_queryset(self):
        user = self.request.user
        class_group =  self.request.query_params.get("class_group")

        qs = Lecture.objects.all()
        if class_group:
           qs = qs.filter(class_group = class_group)

        if user.role == user.Role.DIRECTOR:
            return qs.filter(class_group__organization=user.organization)
        if user.role == user.Role.TEACHER:
            return qs.filter(class_group__teacher_assignments__teacher=user)
        if user.role == user.Role.STUDENT:
            return qs.filter(class_group__enrollments__student=user)
        return qs.none()

    def perform_create(self, serializer):
        serializer.save(teacher=self.request.user)
    
class MaterialViewSet(ModelViewSet):
    serializer_class = MaterialSerializer
    permission_classes = [IsTeacherOrReadOnly]


    def get_queryset(self):
        user = self.request.user
        qs = Material.objects.all()

        if user.role == user.Role.DIRECTOR:
            return qs.filter(lecture__class_group__organization=user.organization)
        if user.role == user.Role.TEACHER:
            return qs.filter(lecture__class_group__teacher_assignments__teacher=user)
        if user.role == user.Role.STUDENT:
            return qs.filter(lecture__class_group__enrollments__student=user)
        return qs.none()
