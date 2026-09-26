from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from django.core.cache import cache
from rest_framework.test import APITestCase

from apps.teachers.models import Teacher
from .models import Student, Group

User = get_user_model()


class StudentsTestCase(APITestCase):
    def setUp(self):

        cache.clear()

        self.admin = User.objects.create_user(
            username='adminuser',
            password='adminuserpassword',
            role=User.Role.ADMIN,
            must_change_password=False
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

        self.student3 = User.objects.create_user(
            username='studentuser3',
            password='studentuser3password',
            role=User.Role.STUDENT,
            must_change_password=False
        )

        self.teacher_user = User.objects.create_user(
            username='teacheruser',
            password='teacheruserpassword',
            role=User.Role.TEACHER,
            must_change_password=False
        )

        self.teacher_user2 = User.objects.create_user(
            username='teacheruser2',
            password='teacheruser2password',
            role=User.Role.TEACHER,
            must_change_password=False
        )

        self.teacher_profile = Teacher.objects.create(
            user=self.teacher_user,
            subject='Python Backend',
            experience=1
        )

        self.teacher_profile2 = Teacher.objects.create(
            user=self.teacher_user2,
            subject='C#',
            experience=2
        )

        self.group = Group.objects.create(
            name='Python',
            teacher=self.teacher_profile,
            monthly_fee=500000
        )


        self.group2 = Group.objects.create(
            name='C#',
            teacher=self.teacher_profile2,
            monthly_fee=450000
        )

        self.student_profile = Student.objects.create(
            user=self.student, group=self.group, parent_phone='+998911234567'
        )

        self.student_profile2 = Student.objects.create(
            user=self.student2, group=self.group, parent_phone='+998997776666'
        )

    def get_result(self, response):
        data = response.data
        if isinstance(data, dict) and 'results' in data:
            return data['results']
        return data

    def test_admin_can_register_student(self):
        self.client.force_authenticate(user=self.admin)

        data = {
            "username": "studentuserbek",
            "first_name": "student_first_name",
            "last_name": "student_last_name",
            "group": self.group.pk,
            "parent_phone": '+998997776666'
        }

        response = self.client.post(reverse('student-register'), data=data, format='json')

        user = User.objects.get(username="studentuserbek")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(user.role, User.Role.STUDENT)
        self.assertTrue(user.must_change_password)
        self.assertTrue(Student.objects.filter(user=user).exists())
        self.assertTrue(user.check_password(response.data['temporary_password']))

    def test_student_can_view_own_profile(self):
        self.client.force_authenticate(user=self.student)

        response = self.client.get(
            reverse('students-detail', kwargs={'pk': self.student_profile.pk}), format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_student_cannot_view_others(self):
        self.client.force_authenticate(user=self.student)

        response = self.client.get(
            reverse('students-detail', kwargs={'pk': self.student_profile2.pk}), format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_student_can_edit_parent_phone(self):
        self.client.force_authenticate(user=self.student)

        data = {"parent_phone": "+998977774455"}

        response = self.client.patch(
            reverse('students-detail', kwargs={'pk': self.student_profile.pk}),
            data=data, format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.student_profile.refresh_from_db()
        self.assertEqual(self.student_profile.parent_phone, '+998977774455')

    def test_student_cannot_edit_others(self):
        self.client.force_authenticate(user=self.student)

        data = {"parent_phone": "+998977774455"}

        response = self.client.patch(
            reverse('students-detail', kwargs={'pk': self.student_profile2.pk}),
            data=data, format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.student_profile2.refresh_from_db()
        self.assertEqual(self.student_profile2.parent_phone, '+998997776666')

    def test_student_cannot_edit_own_group(self):
        self.client.force_authenticate(user=self.student)

        data = {'group': self.group2.pk}

        response = self.client.patch(
            reverse('students-detail', kwargs={'pk': self.student_profile.pk}),
            data=data, format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.student_profile.refresh_from_db()
        self.assertEqual(self.student_profile.group, self.group)

    def test_student_cannot_delete_others(self):
        self.client.force_authenticate(user=self.student)

        response = self.client.delete(
            reverse('students-detail', kwargs={'pk': self.student_profile2.pk}), format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Student.objects.filter(pk=self.student_profile2.pk).exists())

    def test_admin_can_delete_and_edit_any(self):
        self.client.force_authenticate(user=self.admin)

        data = {'group': self.group2.pk}

        response = self.client.patch(
            reverse('students-detail', kwargs={'pk': self.student_profile.pk}),
            data=data, format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.student_profile.refresh_from_db()
        self.assertEqual(self.student_profile.group, self.group2)

        response2 = self.client.delete(
            reverse('students-detail', kwargs={'pk': self.student_profile2.pk}), format='json'
        )

        self.assertEqual(response2.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Student.objects.filter(pk=self.student_profile2.pk).exists())

    def test_student_list_shows_only_own(self):
        self.client.force_authenticate(user=self.student)

        response = self.client.get(reverse('students-list'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = self.get_result(response)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['id'], self.student_profile.pk)

    def test_student_must_change_password(self):
        new_user = User.objects.create_user(
            username='newstudent', password='123456789',
            role=User.Role.STUDENT
        )

        self.client.force_authenticate(user=new_user)

        response = self.client.get(reverse('students-list'), format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_teacher_can_retrieve_group_student(self):
        self.client.force_authenticate(user=self.teacher_user)

        response = self.client.get(
            reverse('students-detail', kwargs={'pk': self.student_profile.pk}), format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_teacher_cannot_retrieve_other_group_student(self):
        self.client.force_authenticate(user=self.teacher_user)

        new_student = Student.objects.create(
            user=self.student3, group=self.group2, parent_phone='+998998887766'
        )

        response = self.client.get(
            reverse('students-detail', kwargs={'pk': new_student.pk}), format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_teacher_cannot_edit_student(self):
        self.client.force_authenticate(user=self.teacher_user)

        data = {'parent_phone': '+998997776699'}

        response = self.client.patch(
            reverse('students-detail', kwargs={'pk': self.student_profile.pk}),
            data=data, format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.student_profile.refresh_from_db()
        self.assertEqual(self.student_profile.parent_phone, '+998911234567')

    def test_admin_can_create_group(self):
        self.client.force_authenticate(user=self.admin)

        data = {'name':'barcelona', 'teacher':self.teacher_profile.pk, 'monthly_fee':450000}

        response = self.client.post(reverse('group-list'), data=data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Group.objects.filter(name='barcelona').exists())

    def test_admin_can_edit_group(self):
        self.client.force_authenticate(user=self.admin)

        data = {
            'name':'Python Beginner'
        }

        response = self.client.patch(reverse('group-detail', kwargs={'pk':self.group.pk}), data=data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(Group.objects.filter(name='Python Beginner').exists())

    def test_admin_can_delete_group(self):
        self.client.force_authenticate(user=self.admin)

        new_group = Group.objects.create(name='game-dev', teacher=self.teacher_profile2, monthly_fee=500000)

        response = self.client.delete(reverse('group-detail', kwargs={'pk':new_group.pk}), format='json')

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Group.objects.filter(name='game-dev').exists())

    def test_group_teacher_cannot_edit_group(self):
        self.client.force_authenticate(user=self.teacher_user)

        data = {
            'name':'AWS'
        }

        response = self.client.patch(reverse('group-detail', kwargs={'pk':self.group.pk}), data=data, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Group.objects.filter(name='Python').exists())

    def test_student_cannot_edit_group(self):
        self.client.force_authenticate(user=self.student)

        data = {
            'name':'Linux'
        }    

        response = self.client.patch(reverse('group-detail', kwargs={'pk':self.group.pk}), data=data, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Group.objects.filter(name='Python').exists())

    def test_group_teacher_can_list_group(self):
        self.client.force_authenticate(user=self.teacher_user)

        response = self.client.get(reverse('group-list'), format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_student_can_list_enlisted_groups(self):
        self.client.force_authenticate(user=self.student)

        response = self.client.get(reverse('group-list'), format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
