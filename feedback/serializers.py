from rest_framework import serializers
from django.utils import timezone
from datetime import timedelta
from .models import Feedback


COOLDOWN_DAYS = 7

class FeedbackCreateSerializer(serializers.Serializer):
    subject_knowledge = serializers.IntegerField(min_value=1, max_value=5)
    doubt_resolution = serializers.IntegerField(min_value=1, max_value=5)
    teaching_quality = serializers.IntegerField(min_value=1, max_value=5)
    practical_learning = serializers.IntegerField(min_value=1, max_value=5)
    comments = serializers.CharField(required=False, allow_blank=True, default='')

    def validate(self, data):
        student = self.context['request'].user
        enrollment = getattr(student, 'enrollment', None)

        if not enrollment:
            raise serializers.ValidationError("You are not enrolled in any class.")

        class_group = enrollment.class_group
        assignment = class_group.teacher_assignments.select_related('teacher').first()

        if not assignment:
            raise serializers.ValidationError("Your class doesn't have a teacher assigned yet.")
        if not class_group.current_program:
            raise serializers.ValidationError("Your class doesn't have an active program yet.")

        teacher = assignment.teacher
        program = class_group.current_program
        

        last_feedback = Feedback.objects.filter(
            teacher=teacher, program=program, student = student, class_group=class_group
        ).first()
   

        if last_feedback:
            eligible_at = last_feedback.created_at + timedelta(days=COOLDOWN_DAYS)
            if timezone.now() < eligible_at:
                raise serializers.ValidationError(
                    f"You can submit feedback again on {eligible_at.strftime('%d %b %Y')}."
                )
        
        data['student'] = student
        data['teacher'] = teacher
        data['class_group'] = class_group
        data['program'] = program
      
        return data

    def create(self, validated_data):
        return Feedback.objects.create(**validated_data)

class FeedbackListSerializer(serializers.ModelSerializer):
    teacher_name = serializers.SerializerMethodField()
    class_group_label = serializers.SerializerMethodField()
    program_title = serializers.CharField(source='program.title', read_only = True)

    class Meta :
        model = Feedback
        fields = ["id", "teacher_name", "class_group_label", "program_title", "subject_knowledge", "doubt_resolution", "teaching_quality", "practical_learning", "comments", "created_at"]

    def get_teacher_name(self, obj):
        full_name = f"{obj.teacher.first_name} {obj.teacher.last_name}".strip()
        return full_name or obj.teacher.username

    def get_class_group_label(self, obj):
        cg = obj.class_group
        return f"{cg.course} Year {cg.year} - {cg.branch} {cg.section}"
