from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Teacher

User = get_user_model()


class TeacherTestCase(APITestCase):
    def setUp(self):

        cache.clear()

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

        self.teacher_profile = Teacher.objects.create(
            user=self.teacher, subject='Frontend', experience=2
        )
        self.teacher2_profile = Teacher.objects.create(
            user=self.teacher2, subject='DevOps', experience=3
        )

        self.register_data = {
            "username": "teachingperson",
            "first_name": "teaching",
            "last_name": "person",
            "subject": "Js",
            "experience": 2,
        }


    def get_results(self, response):
        data = response.data
        if isinstance(data, dict) and 'results' in data:
            return data['results']
        return data



    def test_admin_can_register_teacher(self):
        self.client.force_authenticate(user=self.admin)

        response = self.client.post(
            reverse('teacher-register'), data=self.register_data, format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('temporary_password', response.data)

        user = User.objects.get(username='teachingperson')
        self.assertEqual(user.role, User.Role.TEACHER)
        self.assertTrue(user.must_change_password)
        self.assertTrue(Teacher.objects.filter(user=user).exists())
    
        self.assertTrue(user.check_password(response.data['temporary_password']))

    def test_teacher_cannot_register_teacher(self):
        self.client.force_authenticate(user=self.teacher)

        response = self.client.post(
            reverse('teacher-register'), data=self.register_data, format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(User.objects.filter(username='teachingperson').exists())

    def test_register_duplicate_username(self):
        self.client.force_authenticate(user=self.admin)
        data = {**self.register_data, "username": self.teacher.username}

        response = self.client.post(
            reverse('teacher-register'), data=data, format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_teacher_can_view_own_profile(self):
        self.client.force_authenticate(user=self.teacher)

        response = self.client.get(
            reverse('teacher-detail', kwargs={'pk': self.teacher_profile.pk})
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_teacher_cannot_view_others_profile(self):
        self.client.force_authenticate(user=self.teacher)

        response = self.client.get(
            reverse('teacher-detail', kwargs={'pk': self.teacher2_profile.pk})
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_admin_can_view_any_teacher(self):
        self.client.force_authenticate(user=self.admin)

        response = self.client.get(
            reverse('teacher-detail', kwargs={'pk': self.teacher_profile.pk})
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_teacher_can_edit_self(self):
        self.client.force_authenticate(user=self.teacher)

        response = self.client.patch(
            reverse('teacher-detail', kwargs={'pk': self.teacher_profile.pk}),
            data={"subject": "math"}, format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.teacher_profile.refresh_from_db()
        self.assertEqual(self.teacher_profile.subject, 'math')

    def test_teacher_cannot_edit_others(self):
        self.client.force_authenticate(user=self.teacher)

        response = self.client.patch(
            reverse('teacher-detail', kwargs={'pk': self.teacher2_profile.pk}),
            data={"subject": "foreign language"}, format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.teacher2_profile.refresh_from_db()
        self.assertEqual(self.teacher2_profile.subject, 'DevOps')

    def test_admin_can_edit_any_teacher(self):
        self.client.force_authenticate(user=self.admin)

        response = self.client.patch(
            reverse('teacher-detail', kwargs={'pk': self.teacher_profile.pk}),
            data={"subject": "Fizika"}, format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.teacher_profile.refresh_from_db()
        self.assertEqual(self.teacher_profile.subject, 'Fizika')

    def test_teacher_cannot_delete_others(self):
        self.client.force_authenticate(user=self.teacher)

        response = self.client.delete(
            reverse('teacher-detail', kwargs={'pk': self.teacher2_profile.pk})
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Teacher.objects.filter(pk=self.teacher2_profile.pk).exists())

    def test_admin_can_delete_teacher(self):
        self.client.force_authenticate(user=self.admin)

        response = self.client.delete(
            reverse('teacher-detail', kwargs={'pk': self.teacher_profile.pk})
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Teacher.objects.filter(pk=self.teacher_profile.pk).exists())

    def test_teacher_list_shows_only_own(self):
        self.client.force_authenticate(user=self.teacher)

        response = self.client.get(reverse('teacher-list'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = self.get_results(response)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['id'], self.teacher_profile.pk)

    def test_admin_list_shows_all(self):
        self.client.force_authenticate(user=self.admin)

        response = self.client.get(reverse('teacher-list'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(self.get_results(response)), 2)

    def test_list_cache_does_not_leak_between_roles(self):
        self.client.force_authenticate(user=self.admin)
        admin_response = self.client.get(reverse('teacher-list'))
        self.assertEqual(len(self.get_results(admin_response)), 2)

        
        self.client.force_authenticate(user=self.teacher)
        teacher_response = self.client.get(reverse('teacher-list'))
        self.assertEqual(len(self.get_results(teacher_response)), 1)
    
    def test_must_change_password_blocks_access(self):
        new_user = User.objects.create_user(
            username='newteacher', password='newteacherpass',
            role=User.Role.TEACHER
        )
        self.client.force_authenticate(user=new_user)

        response = self.client.get(reverse('teacher-list'))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)