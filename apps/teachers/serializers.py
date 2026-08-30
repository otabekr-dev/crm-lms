from rest_framework import serializers
from .models import Teacher
from django.contrib.auth import get_user_model

User = get_user_model()

class TeacherSerializer(serializers.ModelSerializer):

    class Meta:
        model = Teacher
        fields = [
            'id', 'user',
            'subject', 'experience', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


    
    def validate_user(self, value):
        if value.role != User.Role.TEACHER:
            raise serializers.ValidationError(
                'Role must be Teacher'
            )
        existing=Teacher.objects.filter(user=value).first()
        if existing and existing !=self.instance:
            raise serializers.ValidationError(
                'Teacher already assigned'
            )
        return value