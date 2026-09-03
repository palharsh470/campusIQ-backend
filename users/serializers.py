from rest_framework import serializers
from .models import User
from django.db import transaction
from organizations.models import Organization


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "role",
            "organization",
            "first_name",
            "last_name",
        ]


class RegisterOrgSerializer(serializers.Serializer):
    org_name = serializers.CharField(max_length=255)
    type = serializers.CharField(max_length=20)
    username = serializers.CharField(max_length=255)
    email = serializers.EmailField()
    password = serializers.CharField(min_length=8, write_only=True)

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username already taken.")
        return value

    def create(self, validated_data):
        with transaction.atomic():
            org = Organization.objects.create(
                name=validated_data["org_name"], type=validated_data["type"]
            )
            director = User.objects.create_user(
                username=validated_data["username"],
                email=validated_data["email"],
                password=validated_data["password"],
                role=User.Role.DIRECTOR,
                organization=org,
            )
            return director
