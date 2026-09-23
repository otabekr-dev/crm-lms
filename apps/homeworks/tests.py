from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status
from .models import Homework
from django.contrib.auth import get_user_model
from apps.students.models import  Group, Student
from apps.teachers.models import Teacher
from datetime import timedelta
from django.utils import timezone

User = get_user_model()

class HomeWorkTestCase(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            username='admin', password='12345678', must_change_password=False, role=User.Role.ADMIN
        )

        self.student_user = User.objects.create_user(
            username='student', password='12345678', must_change_password=False, role=User.Role.STUDENT
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

        self.student = Student.objects.create(
            user=self.student_user, group=self.group, parent_phone='+998914789632'
        )

        self.future_deadline = (timezone.now() + timedelta(days=7)).isoformat()   
        self.past_deadline = (timezone.now() - timedelta(days=1)).isoformat()   

        self.homework = Homework.objects.create(
            group=self.group, teacher=self.teacher, title='homework1',
            description='homework1 description', deadline=self.future_deadline
        )

    def test_teacher_create_group_homework(self):
        self.client.force_authenticate(user=self.teacher_user)

        data = {
            'group':self.group.pk, 'title':'Django ORM', 
            'description':'1-5 problems',
            'deadline':self.future_deadline
        }

        response = self.client.post(reverse('homework-list'), data=data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Homework.objects.filter(group=self.group.pk, title='Django ORM').exists())

    def test_teacher_cannot_create_others_group_homework(self):
        self.client.force_authenticate(user=self.teacher_user2)    

        data = {
            'group':self.group.pk, 'title':'Django ORM 2',
            'description':'6-10 problems',
            'deadline':self.future_deadline
        }

        response = self.client.post(reverse('homework-list'), data=data, format='json')

        self.assertIn(response.status_code, [status.HTTP_403_FORBIDDEN,status.HTTP_400_BAD_REQUEST])
        self.assertFalse(Homework.objects.filter(group=self.group.pk, title='Django ORM 2').exists())

    def test_admin_create_homework_by_teacher_id(self):
        self.client.force_authenticate(user=self.admin)

        data = {
            'group':self.group.pk, 'teacher':self.teacher.pk,
            'title':'Sqlalchemy ORM', 'description':'1-10 problems',
            'deadline':self.future_deadline
        }

        response = self.client.post(reverse('homework-list'), data=data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            Homework.objects.filter(group=self.group.pk, teacher=self.teacher.pk, title='Sqlalchemy ORM').exists()
        )

    def test_admin_cannot_create_withou_teacher_id(self):
        self.client.force_authenticate(user=self.admin)

        data = {
            'group':self.group.pk,'title':'Fastapi', 
            'description':'fastapi',
            'deadline':self.future_deadline
        }

        response = self.client.post(reverse('homework-list'), data=data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_deadline_in_past_rejected(self):
        self.client.force_authenticate(user=self.admin)

        data = {
            'group':self.group.pk, 'teacher':self.teacher.pk,
            'title':'Models', 'description':'models',
            'deadline':self.past_deadline
        }

        response = self.client.post(reverse('homework-list'), data=data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_teacher_can_edit_own_homework(self):
        self.client.force_authenticate(user=self.teacher_user)

        data = {'title':'Python'}

        response = self.client.patch(reverse('homework-detail', kwargs={'pk':self.homework.pk}), data=data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(Homework.objects.filter(pk=self.homework.pk, title='Python'))

    def test_admin_can_edit_any_homework(self):
        self.client.force_authenticate(user=self.admin)

        data = {'title':'SQL'}

        response = self.client.patch(reverse('homework-detail', kwargs={'pk':self.homework.pk}), data=data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(Homework.objects.filter(pk=self.homework.pk, title='SQL').exists())

    def test_student_can_see_own_group_homework(self):
        self.client.force_authenticate(user=self.student_user)

        response = self.client.get(reverse('homework-list'), format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
