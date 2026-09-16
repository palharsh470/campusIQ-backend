from rest_framework import serializers
from .models import Program, ClassGroup, TeacherAssignment, Enrollment
from django.db import transaction
from users.serializers import UserSerializer

class ProgramSerializer(serializers.ModelSerializer):
    class Meta:
        model = Program
        fields = ["id", "title", "organization", "description", "duration_weeks", "created_at"]
        read_only_fields = ["organization", "created_at"]   


class ClassGroupSerializer(serializers.ModelSerializer):
    current_program_detail = ProgramSerializer(source='current_program', read_only=True)
    assigned_teacher = serializers.SerializerMethodField()

    class Meta:
        model = ClassGroup
        fields = ["id", "course", "year", "branch", "section", "organization", "current_program","current_program_detail", "assigned_teacher", "created_at"]
        read_only_fields = ["organization", "created_at"]

    def validate_current_program(self, value):
        if value is not None:
            director = self.context['request'].user
            if value.organization_id != director.organization_id:
                raise serializers.ValidationError("Program does not belong to your organization.")
        return value

    def get_assigned_teacher(self, obj):
        assignment = obj.teacher_assignments.select_related('teacher').first()
        if not assignment:
            return None
        teacher = assignment.teacher
        full_name = f"{teacher.first_name} {teacher.last_name}".strip()
        return {"id": teacher.id, "name": full_name or teacher.username}

class TeacherAssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeacherAssignment
        fields = ["id", "class_group", "teacher", "assigned_at"]
        read_only_fields = ["assigned_at"]

    def validate(self, data):
        director = self.context['request'].user
        teacher = data['teacher']
        class_group = data['class_group']

        if teacher.role != teacher.Role.TEACHER:
            raise serializers.ValidationError({"teacher": "Selected user is not a teacher."})
        if teacher.organization_id != director.organization_id:
            raise serializers.ValidationError({"teacher": "Teacher does not belong to your organization."})
        if class_group.organization_id != director.organization_id:
            raise serializers.ValidationError({"class_group": "Class group does not belong to your organization."})
        return data

    def create(self, validated_data):
        class_group = validated_data['class_group']
        with transaction.atomic():
            TeacherAssignment.objects.filter(class_group=class_group).delete()
            return super().create(validated_data)



class EnrollmentSerializer(serializers.ModelSerializer):
    student = UserSerializer(read_only=True)
    class_group = ClassGroupSerializer(read_only=True)

    class Meta:
        model = Enrollment
        fields = ["id", "student", "class_group", "enrolled_at"]
        read_only_fields = ["enrolled_at"]
