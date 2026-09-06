from rest_framework import serializers
from .models import Teacher
from django.contrib.auth import get_user_model
from django.db import transaction
import secrets

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


class TeacherRegisterSerializer(serializers.Serializer):
    username = serializers.CharField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    subject = serializers.CharField(max_length=100)
    experience = serializers.IntegerField(default=1)

    def validate(self, attrs):
        if attrs['experience'] < 0:
            raise serializers.ValidationError('Experience cannot be negative')

        return attrs

    @transaction.atomic
    def create(self, validated_data):
        temp_password = secrets.token_urlsafe(8)
        user = User.objects.create_user(
            username=validated_data['username'],
            password=temp_password,
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            role=User.Role.TEACHER
        )

        teacher = Teacher.objects.create(
            user=user,
            subject=validated_data['subject'],
            experience=validated_data.get('experience')
        )

        teacher.temp_password=temp_password
        
        return teacher

    def to_representation(self, instance):
        return {
            'id':instance.id,
            'username':instance.user.username,
            'first_name':instance.user.first_name,
            'subject':instance.subject,
            'experience':instance.experience,
            'temporary_password':instance.temp_password
        }