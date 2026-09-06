from rest_framework import serializers
from .models import Program, ClassGroup, TeacherAssignment, Enrollment


class ProgramSerializer(serializers.ModelSerializer):
    class Meta:
        model = Program
        fields = ["id", "title", "organization", "description", "duration_weeks", "created_at"]
        read_only_fields = ["organization", "created_at"]   # id PK hone ki wajah se already read-only hai


class ClassGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassGroup
        fields = ["id", "course", "year", "branch", "section", "organization", "current_program", "created_at"]
        read_only_fields = ["organization", "created_at"]

    def validate_current_program(self, value):
        if value is not None:
            director = self.context['request'].user
            if value.organization_id != director.organization_id:
                raise serializers.ValidationError("Program does not belong to your organization.")
        return value


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

class EnrollmentSerializer(serializers.ModelSerializer):
    class Meta :
        model = Enrollment
        fields = ["id", "student", "class_group", "enrolled_at"]
        read_only_fields = ["enrolled_at"]

