from rest_framework import serializers
from .models import Assignment, AssignmentAnswer, AssignmentOption, AssignmentQuestion, AssignmentSubmission
from classes.models import TeacherAssignment
from django.db import transaction


class AssignmentOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssignmentOption
        fields = ["id", "text", "is_correct"]

class AssignmentQuestionSerializer(serializers.ModelSerializer):
    options = AssignmentOptionSerializer(many=True)

    class Meta:
        model = AssignmentQuestion
        fields = ["id", "text", "order", "options"]
        read_only_fields = ["order"]

    def validate_options(self, value):
        if len(value) < 2:
            raise serializers.ValidationError("At least 2 options are required.")
        correct_count = sum(1 for o in value if o.get("is_correct"))
        if correct_count != 1:
            raise serializers.ValidationError("Exactly one option must be marked correct.")
        return value


class AssignmentBuilderSerializer(serializers.ModelSerializer):
    questions = AssignmentQuestionSerializer(many=True)

    class Meta:
        model = Assignment
        fields = ["id", "lecture", "title", "questions", "created_at"]
        read_only_fields = ["created_at"]

    def validate_lecture(self, value):
        teacher = self.context['request'].user
        if not TeacherAssignment.objects.filter(teacher=teacher, class_group=value.class_group).exists():
            raise serializers.ValidationError("You are not assigned to this lecture's class.")
        return value

    def create(self, validated_data):
        questions_data = validated_data.pop('questions')
        with transaction.atomic():
            assignment = Assignment.objects.create(**validated_data)
            self._save_questions(assignment, questions_data)
        return assignment

    def update(self, instance, validated_data):
        questions_data = validated_data.pop('questions', None)
        with transaction.atomic():
            instance.title = validated_data.get('title', instance.title)
            instance.save()
            if questions_data is not None:
                instance.questions.all().delete()  
                self._save_questions(instance, questions_data)
        return instance

    def _save_questions(self, assignment, questions_data):
        for i, q_data in enumerate(questions_data):
            options_data = q_data.pop('options')
            question = AssignmentQuestion.objects.create(assignment=assignment, order=i, **q_data)
            AssignmentOption.objects.bulk_create([
                AssignmentOption(question=question, **opt) for opt in options_data
            ])


class AssignmentOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssignmentOption
        fields = ["id", "text", "is_correct"]


class AssignmentQuestionSerializer(serializers.ModelSerializer):
    options = AssignmentOptionSerializer(many=True)

    class Meta:
        model = AssignmentQuestion
        fields = ["id", "text", "order", "options"]
        read_only_fields = ["order"]

    def validate_options(self, value):
        if len(value) < 2:
            raise serializers.ValidationError("At least 2 options are required.")
        correct_count = sum(1 for o in value if o.get("is_correct"))
        if correct_count != 1:
            raise serializers.ValidationError("Exactly one option must be marked correct.")
        return value


class AssignmentBuilderSerializer(serializers.ModelSerializer):
    questions = AssignmentQuestionSerializer(many=True)

    class Meta:
        model = Assignment
        fields = ["id", "lecture", "title", "questions", "created_at"]
        read_only_fields = ["created_at"]

    def validate_lecture(self, value):
        teacher = self.context['request'].user
        if not TeacherAssignment.objects.filter(teacher=teacher, class_group=value.class_group).exists():
            raise serializers.ValidationError("You are not assigned to this lecture's class.")
        return value

    def create(self, validated_data):
        questions_data = validated_data.pop('questions')
        with transaction.atomic():
            assignment = Assignment.objects.create(**validated_data)
            self._save_questions(assignment, questions_data)
        return assignment

    def update(self, instance, validated_data):
        questions_data = validated_data.pop('questions', None)
        with transaction.atomic():
            instance.title = validated_data.get('title', instance.title)
            instance.save()
            if questions_data is not None:
                instance.questions.all().delete() 
                self._save_questions(instance, questions_data)
        return instance

    def _save_questions(self, assignment, questions_data):
        for i, q_data in enumerate(questions_data):
            options_data = q_data.pop('options')
            question = AssignmentQuestion.objects.create(assignment=assignment, order=i, **q_data)
            AssignmentOption.objects.bulk_create([
                AssignmentOption(question=question, **opt) for opt in options_data
            ])


class AssignmentOptionTakeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssignmentOption
        fields = ["id", "text"]  


class AssignmentQuestionTakeSerializer(serializers.ModelSerializer):
    options = AssignmentOptionTakeSerializer(many=True)

    class Meta:
        model = AssignmentQuestion
        fields = ["id", "text", "order", "options"]


class AssignmentTakeSerializer(serializers.ModelSerializer):
    questions = AssignmentQuestionTakeSerializer(many=True)

    class Meta:
        model = Assignment
        fields = ["id", "lecture", "title", "questions", "created_at"]

class AssignmentAnswerInputSerializer(serializers.Serializer):
    question = serializers.PrimaryKeyRelatedField(queryset=AssignmentQuestion.objects.all())
    selected_option = serializers.PrimaryKeyRelatedField(queryset=AssignmentOption.objects.all())

class AssignmentSubmitSerializer(serializers.Serializer):
    answers = AssignmentAnswerInputSerializer(many=True)

    def validate(self, data):
        assignment = self.context['assignment']
        question_ids = set(assignment.questions.values_list('id', flat=True))
        submitted_ids = {a['question'].id for a in data['answers']}

        if submitted_ids != question_ids:
            raise serializers.ValidationError("Please answer all questions.")

        for a in data['answers']:
            if a['selected_option'].question_id != a['question'].id:
                raise serializers.ValidationError("Selected option doesn't belong to its question.")

        return data