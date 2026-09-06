from rest_framework import serializers
from .models import Group, Student
from django.contrib.auth import get_user_model
import secrets
from django.db import transaction

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
        

class StudentRegisterSerializer(serializers.Serializer):
    username = serializers.CharField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()        
    group = serializers.PrimaryKeyRelatedField(queryset=Group.objects.all())
    parent_phone = serializers.CharField()


    @transaction.atomic
    def create(self, validated_data):
        temp_password = secrets.token_urlsafe(8)
        user = User.objects.create_user(
            username=validated_data['username'],
            password=temp_password,
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            role=User.Role.STUDENT
        )

        student = Student.objects.create(
            user=user,
            group=validated_data['group'],
            parent_phone=validated_data['parent_phone']
        )

        student.temp_password = temp_password

        return student

    def to_representation(self, instance):
        return {
            'id':instance.id,
            'username':instance.user.username,
            'first_name':instance.user.first_name,
            'group':instance.group.name,
            'parent_phone':instance.parent_phone,
            'temp_password':instance.temp_password
        }