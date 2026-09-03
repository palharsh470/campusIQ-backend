from django.shortcuts import render
from rest_framework import generics, permissions, status
from .serializers import RegisterOrgSerializer, UserSerializer
from rest_framework.response import Response
from rest_framework.views import APIView


class RegisterOrgView(generics.CreateAPIView):
    print("Registration started")
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

