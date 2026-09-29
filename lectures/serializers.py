from rest_framework import serializers
from .models import Lecture, Material
from classes.models import TeacherAssignment
from django.utils import timezone
    
class MaterialSerializer(serializers.ModelSerializer):
    class Meta :
        model = Material
        fields = ["id", "title", "resource","lecture", "created_at"]
        read_only_fields = ["created_at"]    

    def validate_lecture(self, value):
        teacher = self.context['request'].user
        if not TeacherAssignment.objects.filter(teacher=teacher, class_group = value.class_group) :
            return serializers.ValidationError("You are not assigned to this lecture's class.")
        return value

class LeactureSerializer(serializers.ModelSerializer):
    materials = MaterialSerializer(many = True, read_only=True)
    class Meta :
        model = Lecture
        fields = ["id", "class_group", "program", "teacher","day_number", "title", "video", "url", "description","materials", "created_at"]
        read_only_fields = ["teacher","program", "created_at"]

    def validate_class_group(self, value):
        teacher = self.context['request'].user
        if not TeacherAssignment.objects.filter(teacher=teacher, class_group=value).exists():
            raise serializers.ValidationError("You are not assigned to this class group.")
        if not value.current_program:
            raise serializers.ValidationError("This class doesn't have an active program yet.")
        if not value.current_program.duration_days:
            raise serializers.ValidationError("This program doesn't have a day-wise duration set yet.")
        return value

    def validate(self, data):
        class_group = data.get('class_group') or getattr(self.instance, 'class_group', None)
        day_number = data.get('day_number') or getattr(self.instance, 'day_number', None)

        if class_group and day_number and class_group.current_program:
            max_days = class_group.current_program.duration_days
            if max_days and not (1 <= day_number <= max_days):
                raise serializers.ValidationError({"day_number": f"Day must be between 1 and {max_days}."})

        if class_group.program_started_at:
            today = timezone.now().date()
            max_unlocked_day = (today - class_group.program_started_at).days + 1
            if day_number > max_unlocked_day:
                raise serializers.ValidationError({
                    "day_number": f"Day {day_number} hasn't arrived yet. You can upload up to Day {max_unlocked_day}."
                })
            
        return data

    def validate_youtube_url(self, value):
        if 'youtube.com' not in value and 'youtu.be' not in value:
            raise serializers.ValidationError("Please provide a valid YouTube link.")
        return value