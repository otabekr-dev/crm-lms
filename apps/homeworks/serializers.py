from rest_framework import serializers
from .models import Homework
from django.utils import timezone
from apps.teachers.models import Teacher
from django.contrib.auth import get_user_model

User = get_user_model()

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

    def validate_group(self, value):
        request = self.context['request']

        if request.user.role == User.Role.TEACHER:
            if value.teacher.user != request.user:
                raise serializers.ValidationError('Bu guruh sizga tegishli emas')

        return value    