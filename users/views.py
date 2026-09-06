from django.shortcuts import render
from rest_framework import generics, permissions, status
from .serializers import RegisterOrgSerializer, UserSerializer, CreateStudentSerializer, CreateTeacherSerializer
from rest_framework.response import Response
from rest_framework.views import APIView
from .permissions import IsDirector

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


class CreateTeacherView(generics.CreateAPIView):
    serializer_class = CreateTeacherSerializer
    permission_classes = [IsDirector]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        teacher = serializer.save()
        return Response(UserSerializer(teacher).data, status=status.HTTP_201_CREATED)


class CreateStudentView(generics.CreateAPIView):
    serializer_class = CreateStudentSerializer
    permission_classes = [IsDirector]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        student = serializer.save()
        return Response(UserSerializer(student).data, status=status.HTTP_201_CREATED)

