from rest_framework import serializers
from .models import Group, Student
from django.contrib.auth import get_user_model
import secrets
from django.db import transaction
from core.validators import validate_uzb_numbers

User = get_user_model()

class StudentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Student
        fields = ['id', 'user', 'group','parent_phone']
        read_only_fields = ['id', 'created_at']
        extra_kwargs = {'paren_phone':{'validators':[validate_uzb_numbers]}}

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

    def validate_group(self, value):
        request = self.context['request']
        if request.user.role != User.Role.ADMIN:
            raise serializers.ValidationError('Only admin can change student group')
        return value


    
class GroupSerializer(serializers.ModelSerializer):

    class Meta:
        model = Group
        fields = ['id', 'name', 'teacher', 'monthly_fee']
        read_only_fields = ['id', 'created_at']
        

class StudentRegisterSerializer(serializers.Serializer):
    username = serializers.CharField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()        
    group = serializers.PrimaryKeyRelatedField(queryset=Group.objects.all())
    parent_phone = serializers.CharField(validators=[validate_uzb_numbers])

    def validate_username(self, value):
        if Student.objects.filter(user__username=value).exists():
            raise serializers.ValidationError('Username already taken')  
        return value  

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
            'temporary_password':instance.temp_password
        }