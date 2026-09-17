from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from rest_framework import status
from django.urls import reverse

User = get_user_model()


class AuthenticationTestCase(APITestCase):

    def setUp(self):
        self.admin = User.objects.create_user(
            username='adminuser', password='adminuserpassword', role=User.Role.ADMIN
        )
        self.teacher = User.objects.create_user(
            username='teacheruser', password='teacheruserpassword', role=User.Role.TEACHER
        )
        self.unchanged_password_user = User.objects.create_user(
            username='unchangedpassworduser',
            password='unchangedpassworduserpassword',
            must_change_password=True,
            role=User.Role.TEACHER,
        )

    def test_login_with_correct_credentials(self):
        data = {"username": "adminuser", "password": "adminuserpassword"}
        response = self.client.post(reverse('login'), data=data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)

    def test_login_with_wrong_credentials(self):
        data = {"username": "adminuser", "password": "2132135654"}
        response = self.client.post(reverse('login'), data=data, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertNotIn('access', response.data)

    def test_register_only_admin(self):
        self.client.force_authenticate(user=self.admin)

        data = {
            "first_name": "Aziz",
            "last_name": "Aliyev",
            "username": "aziz_user",
            "password": "securepass123",
            "confirm": "securepass123",
            "role": "TEACHER",
        }

        response = self.client.post(reverse('register'), data=data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.filter(username='aziz_user').count(), 1)

    def test_cannot_register(self):
        self.client.force_authenticate(user=self.teacher)

        data = {
            "first_name": "Aziz",
            "last_name": "Aliyev",
            "username": "azizbek_user",
            "password": "securepass123",
            "confirm": "securepass123",
            "role": "TEACHER",
        }

        response = self.client.post(reverse('register'), data=data, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(User.objects.filter(username='azizbek_user').count(), 0)

    def test_must_change_password_blocks_other_endpoints(self):
        self.client.force_authenticate(user=self.unchanged_password_user)
        response = self.client.get(reverse('teacher-list'), format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_can_change_unchanged_password(self):
        self.client.force_authenticate(user=self.unchanged_password_user)

        data = {
            "old_password": "unchangedpassworduserpassword",
            "new_password": "12345678",
            "confirm": "12345678",
        }

        response = self.client.post(reverse('change-password'), data=data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(
            User.objects.filter(username='unchangedpassworduser', must_change_password=False).exists()
        )