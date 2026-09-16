from rest_framework import serializers
from .models import Lecture, Material
    
class MaterialSerializer(serializers.ModelSerializer):
    class Meta :
        model = Material
        fields = ["id", "title", "resource","lecture", "created_at"]
        read_only_fields = ["created_at"]         

class LeactureSerializer(serializers.ModelSerializer):
    class Meta :
        model = Lecture
        fields = ["id", "title", "video", "url","class_group", "description", "created_at"]
        read_only_fields = ["created_at"]