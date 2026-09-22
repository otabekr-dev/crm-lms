from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status
from .models import Homework
from django.contrib.auth import get_user_model
from apps.students.models import  Group
from apps.teachers.models import Teacher

User = get_user_model()

class HomeWorkTestCase(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            username='admin', password='12345678', must_change_password=False, role=User.Role.ADMIN
        )

        
        self.teacher_user = User.objects.create_user(
            username='teacher', password='123456789', must_change_password=False, role=User.Role.TEACHER
        )

        self.teacher_user2 = User.objects.create_user(
            username='teacher2', password='123456789', must_change_password=False, role=User.Role.TEACHER
        )

        self.teacher = Teacher.objects.create(
            user=self.teacher_user, subject='cybersecurity', experience=3
        )

        self.teacher2 = Teacher.objects.create(
            user=self.teacher_user2, subject='cybersecurity', experience=3
        )

        self.group = Group.objects.create(
            name='CybSec', teacher=self.teacher, monthly_fee=400000
        )

        self.group2 = Group.objects.create(
            name='CybSec', teacher=self.teacher2, monthly_fee=400000
        )

    def test_teacher_create_group_homework(self):
        self.client.force_authenticate(self.teacher_user)
        ...