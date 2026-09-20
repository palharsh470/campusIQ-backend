from django.db.models import Q
from rest_framework import serializers
from lectures.models import Lecture
from skills.models import SkillTag
from .models import Doubt, DoubtMessage


class DoubtCreateSerializer(serializers.Serializer):
    lecture = serializers.PrimaryKeyRelatedField(queryset=Lecture.objects.all(), required=False, allow_null=True)
    topic = serializers.PrimaryKeyRelatedField(queryset=SkillTag.objects.all(), required=False, allow_null=True)
    title = serializers.CharField(max_length=255)
    question = serializers.CharField()
    attachment = serializers.ImageField(required=False, allow_null=True)

    def validate(self, data):
        student = self.context['request'].user
        enrollment = getattr(student, 'enrollment', None)
        if not enrollment:
            raise serializers.ValidationError("You are not enrolled in any class.")

        class_group = enrollment.class_group
        lecture = data.get('lecture')
        if lecture and lecture.class_group_id != class_group.id:
            raise serializers.ValidationError({"lecture": "This lecture doesn't belong to your class."})

        data['class_group'] = class_group
        data['raised_by'] = student
        return data

    def create(self, validated_data):
        return Doubt.objects.create(**validated_data)


class DoubtMessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.SerializerMethodField()
    sender_role = serializers.CharField(source='sender.role', read_only=True)
    like_count = serializers.IntegerField(read_only=True, default=0)
    is_liked_by_me = serializers.SerializerMethodField()

    class Meta:
        model = DoubtMessage
        fields = [
            "id", "text", "attachment", "sender_name", "sender_role",
            "is_accepted", "like_count", "is_liked_by_me", "created_at",
        ]
        read_only_fields = ["created_at", "is_accepted"]

    def get_sender_name(self, obj):
        full_name = f"{obj.sender.first_name} {obj.sender.last_name}".strip()
        return full_name or obj.sender.username

    def get_is_liked_by_me(self, obj):
        request = self.context.get('request')
        if not request:
            return False
        return obj.likes.filter(user=request.user).exists()


class DoubtListSerializer(serializers.ModelSerializer):
    raised_by_name = serializers.SerializerMethodField()
    topic_name = serializers.CharField(source='topic.name', read_only=True, default=None)
    reply_count = serializers.IntegerField(read_only=True, default=0)

    class Meta:
        model = Doubt
        fields = ["id", "title", "question", "topic_name", "status", "raised_by_name", "reply_count", "created_at"]

    def get_raised_by_name(self, obj):
        full_name = f"{obj.raised_by.first_name} {obj.raised_by.last_name}".strip()
        return full_name or obj.raised_by.username


class DoubtDetailSerializer(serializers.ModelSerializer):
    raised_by_name = serializers.SerializerMethodField()
    resolved_by_name = serializers.SerializerMethodField()
    class_group_label = serializers.SerializerMethodField()
    lecture_title = serializers.CharField(source='lecture.title', read_only=True, default=None)
    topic_name = serializers.CharField(source='topic.name', read_only=True, default=None)
    messages = DoubtMessageSerializer(many=True, read_only=True)
    like_count = serializers.IntegerField(read_only=True, default=0)
    is_liked_by_me = serializers.SerializerMethodField()

    class Meta:
        model = Doubt
        fields = [
            "id", "class_group", "class_group_label", "lecture", "lecture_title", "topic", "topic_name",
            "title", "question", "attachment", "status", "raised_by_name", "resolved_by_name",
            "resolved_at", "views_count", "like_count", "is_liked_by_me", "messages", "created_at",
        ]

    def get_raised_by_name(self, obj):
        full_name = f"{obj.raised_by.first_name} {obj.raised_by.last_name}".strip()
        return full_name or obj.raised_by.username

    def get_resolved_by_name(self, obj):
        if not obj.resolved_by:
            return None
        full_name = f"{obj.resolved_by.first_name} {obj.resolved_by.last_name}".strip()
        return full_name or obj.resolved_by.username

    def get_class_group_label(self, obj):
        cg = obj.class_group
        return f"{cg.course} Year {cg.year} - {cg.branch} {cg.section}"

    def get_is_liked_by_me(self, obj):
        request = self.context.get('request')
        if not request:
            return False
        return obj.likes.filter(user=request.user).exists()