from rest_framework.test import APITestCase
from .models import Student, Group
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from apps.teachers.models import Teacher

User = get_user_model()


class StudentsTestCase(APITestCase):
    def setUp(self):

        self.admin = User.objects.create_user(
            username='adminuser',
            password='adminuserpassword',
            role=User.Role.ADMIN
        )

        self.student = User.objects.create_user(
            username='studentuser',
            password='studentuserpassword',
            role=User.Role.STUDENT,
            must_change_password=False
        )

        self.student2 = User.objects.create_user(
            username='studentuser2',
            password='studentuserpassword',
            role=User.Role.STUDENT,
            must_change_password=False
        )

        self.teacher_user = User.objects.create_user(
            username='teacheruser',
            password='teacheruserpassword',
            role=User.Role.TEACHER,
            must_change_password=False
        )

        self.teacher = Teacher.objects.create(
            user=self.teacher_user,
            subject='Python Backend',
            experience=1
        )

        self.group = Group.objects.create(
            name='Python',
            teacher=self.teacher,
            monthly_fee=500000.00
        )

    def test_register_student_admin_only(self):
        self.client.force_authenticate(user=self.admin)

        data = {
            "username":"studentuserbek",
            "first_name":"student_first_name",
            "last_name":"student_last_name",
            "group":self.group.pk,
            "parent_phone":'+998997776666'
        }

        response = self.client.post(reverse('student-register'), data=data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('temporary_password', response.data)
        self.assertEqual(User.objects.filter(username='studentuserbek').count(), 1)

    def test_student_can_view_own_profile(self):
        self.client.force_authenticate(user=self.student)

        student = Student.objects.create(
            user=self.student,
            group=self.group,
            parent_phone='+998979777997'
        )        

        response = self.client.get(reverse('students-detail', kwargs={'pk':student.pk}), format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_student_cannot_view_others(self):
        self.client.force_authenticate(user=self.student)

        new_student = Student.objects.create(
            user=self.student2,
            group=self.group,
            parent_phone='+998999999999'
        )

        response = self.client.get(reverse('students-detail', kwargs={'pk':new_student.pk}), format='json')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

