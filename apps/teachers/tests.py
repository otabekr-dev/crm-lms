from django.urls import reverse
from rest_framework.test import APITestCase
from .models import Teacher
from django.contrib.auth import get_user_model
from rest_framework import status

User = get_user_model()

class TeacherTestCase(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            username='reyo77', password='reyo77pass',
            role=User.Role.ADMIN, must_change_password=False
        )
        self.teacher = User.objects.create_user(
            username="o'qituvchi", password="o'qituvchipassword",
            role=User.Role.TEACHER, must_change_password=False
        )
        self.teacher2 = User.objects.create_user(
            username='teacher', password='teacherpassword',
            role=User.Role.TEACHER, must_change_password=False
        )

    def test_register_teacher_admin_only(self):
        self.client.force_authenticate(user=self.admin)
        data = {
            "username": "teachingperson", "first_name": "teaching",
            "last_name": "person", "subject": "Js", "experience": 2
        }
        response = self.client.post(reverse('teacher-register'), data=data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username='teachingperson').exists())
        self.assertIn('temporary_password', response.data)
        self.assertEqual(User.objects.filter(username='teachingperson').count(), 1)

    def test_teacher_cannot_create_teacher(self):
        self.client.force_authenticate(user=self.teacher)
        data = {
            "username": "teachingperson2", "first_name": "teaching",
            "last_name": "person", "subject": "NJs", "experience": 2
        }
        response = self.client.post(reverse('teacher-register'), data=data, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(User.objects.filter(username='teachingperson2').exists())

    def test_teacher_can_view_own_profile(self):
        self.client.force_authenticate(user=self.teacher)
        teacher = Teacher.objects.create(user=self.teacher, subject='Frontend', experience=2)

        response = self.client.get(reverse('teacher-detail', kwargs={'pk': teacher.pk}), format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_teacher_cannot_view_others_profile(self):
        self.client.force_authenticate(user=self.teacher)
        new_teacher = Teacher.objects.create(user=self.teacher2, subject='Full Stack', experience=2)

        response = self.client.get(reverse('teacher-detail', kwargs={'pk': new_teacher.pk}), format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_view_any_teacher(self):
        self.client.force_authenticate(user=self.admin)
        teacher = Teacher.objects.create(user=self.teacher, subject='Frontend', experience=2)

        response = self.client.get(reverse('teacher-detail', kwargs={'pk': teacher.pk}), format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_teacher_can_edit_self(self):
        self.client.force_authenticate(user=self.teacher)
        new_teacher = Teacher.objects.create(user=self.teacher, subject='Frontend', experience=2)

        data = {"subject": "math"}
        response = self.client.patch(reverse('teacher-detail', kwargs={'pk': new_teacher.pk}), data=data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Teacher.objects.filter(pk=new_teacher.pk, subject='math').count(), 1)

    def test_teacher_cannot_delete_others(self):
        self.client.force_authenticate(user=self.teacher)
        new_teacher = Teacher.objects.create(user=self.teacher2, subject='UI/UX', experience=2)

        response = self.client.delete(reverse('teacher-detail', kwargs={'pk': new_teacher.pk}), format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Teacher.objects.filter(pk=new_teacher.pk).exists())