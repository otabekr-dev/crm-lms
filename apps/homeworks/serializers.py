from rest_framework import serializers
from .models import Homework
from django.utils import timezone
from apps.teachers.models import Teacher

class HomeworkSerializer(serializers.ModelSerializer):
    teacher = serializers.PrimaryKeyRelatedField(
        queryset=Teacher.objects.all(),
        required=False
    )
    class Meta:
        model = Homework
        fields = [
            'id', 'group', 'teacher',
            'title', 'description', 'deadline',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']

    def validate_deadline(self, value):
        if value <= timezone.now():
            raise serializers.ValidationError("O'tmishdagi vaqtga deadline quyib bulmaydi")
        return value