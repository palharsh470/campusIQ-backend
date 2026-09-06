from rest_framework import serializers
from .models import User
from django.db import transaction
from organizations.models import Organization
from classes.models import ClassGroup, Enrollment

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


class CreateTeacherSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)
    first_name = serializers.CharField(max_length=150, required=False, allow_blank=True)
    last_name = serializers.CharField(max_length=150, required=False, allow_blank=True)

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username already taken.")
        return value

    def create(self, validated_data):
        director = self.context['request'].user
        return User.objects.create_user(
            **validated_data,
            role=User.Role.TEACHER,
            organization=director.organization,
        )


class CreateStudentSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)
    first_name = serializers.CharField(max_length=150, required=False, allow_blank=True)
    last_name = serializers.CharField(max_length=150, required=False, allow_blank=True)
    class_group_id = serializers.IntegerField()

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username already taken.")
        return value

    def validate_class_group_id(self, value):
        director = self.context['request'].user
        print(value)
        print(director.organization)
        if not ClassGroup.objects.filter(id=value, organization=director.organization).exists():
            raise serializers.ValidationError("Class group not found in your organization.")
        return value

    def create(self, validated_data):
        director = self.context['request'].user
        class_group_id = validated_data.pop('class_group_id')
        with transaction.atomic():
            student = User.objects.create_user(
                **validated_data,
                role=User.Role.STUDENT,
                organization=director.organization,
            )
            Enrollment.objects.create(student=student, class_group_id=class_group_id)
        return student