from rest_framework import serializers
from .models import Group, Student
from django.contrib.auth import get_user_model

User = get_user_model()

class StudentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Student
        fields = ['id', 'user', 'group','parent_phone']
        read_only_fields = ['id', 'created_at']

    def validate_user(self, value):
        if value.role != User.Role.STUDENT:
            raise serializers.ValidationError(
                'Role must be Student'
            )
        existing = Student.objects.filter(user=value).first()
        if existing and existing != self.instance:
            raise serializers.ValidationError(
                'Student already assigned'
            )
        return value

class GroupSerializer(serializers.ModelSerializer):

    class Meta:
        model = Group
        fields = ['id', 'name', 'teacher']
        read_only_fields = ['id', 'created_at']
        