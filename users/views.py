from django.shortcuts import render
from rest_framework import generics, permissions, status
from .serializers import RegisterOrgSerializer, UserSerializer, CreateStudentSerializer, TeacherSerializer
from rest_framework.response import Response
from rest_framework.views import APIView
from .permissions import IsDirector
from rest_framework import viewsets
from .models import User

class RegisterOrgView(generics.CreateAPIView):
    serializer_class = RegisterOrgSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        director = serializer.save()
        return Response(UserSerializer(director).data, status=status.HTTP_201_CREATED)

class MeView(APIView):
    permission_classes=[permissions.IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data, status=status.HTTP_200_OK)


class TeacherView(viewsets.ModelViewSet):
    serializer_class = TeacherSerializer
    permission_classes = [IsDirector]

    def get_queryset(self):
        return User.objects.filter(
            organization=self.request.user.organization,
            role=User.Role.TEACHER,
        )

    def perform_create(self, serializer):
        serializer.save(role=User.Role.TEACHER, organization=self.request.user.organization)


class CreateStudentView(generics.CreateAPIView):
    serializer_class = CreateStudentSerializer
    permission_classes = [IsDirector]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        student = serializer.save()
        return Response(UserSerializer(student).data, status=status.HTTP_201_CREATED)

