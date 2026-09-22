from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status
from .models import Attendance
from unittest.mock import patch
from django.contrib.auth import get_user_model
from apps.students.models import Student, Group
from apps.teachers.models import Teacher

User = get_user_model()

class AttendenceTestCase(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            username='admin', password='12345678', must_change_password=False, role=User.Role.ADMIN
        )

        self.student_user = User.objects.create_user(
            username='student', password='12341234', must_change_password=False, role=User.Role.STUDENT
        )

        self.student_user2 = User.objects.create_user(
            username='student2', password='12341234', must_change_password=False, role=User.Role.STUDENT
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
            user=self.student_user, group=self.group, parent_phone='+998997774411'
        )

        self.student2 = Student.objects.create(
            user=self.student_user2, group=self.group2, parent_phone='+998997774411'
        )

        self.attendance = Attendance.objects.create(
            student=self.student, group=self.group, date='2026-09-22',
            status=Attendance.StatusChoice.ABSENT
        )

    def test_teacher_can_post_attendance_own_group(self):
        self.client.force_authenticate(user=self.teacher_user)

        data = {
            'student':self.student.pk, 'group':self.group.pk, 'date':'2026-09-22',
            'status':Attendance.StatusChoice.PRESENT
        }

        response = self.client.post(reverse('attendance-list'), data=data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Attendance.objects.filter(student=self.student.pk, date='2026-09-22').exists())

    def test_teacher_cannot_post_attendance_other_group(self):
        self.client.force_authenticate(user=self.teacher_user)

        data = {
            'student':self.student2.pk, 'group':self.group2.pk, 'date':'2026-09-22',
            'status':Attendance.StatusChoice.PRESENT
        }

        response = self.client.post(reverse('attendance-list'), data=data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(Attendance.objects.filter(student=self.student2.pk, date='2026-09-22').exists())

    def test_cannot_post_future_attendance(self):
        self.client.force_authenticate(user=self.admin)

        data = {
            'student':self.student.pk, 'group':self.group.pk, 'date':'2026-12-31',
            'status':Attendance.StatusChoice.LATE
        }

        response = self.client.post(reverse('attendance-list'), data=data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(Attendance.objects.filter(student=self.student.pk, date='2026-12-31').exists())

    def test_cannot_post_past_attendance(self):
        self.client.force_authenticate(user=self.admin)

        data = {
            'student':self.student.pk, 'group':self.group.pk, 'date':'2026-09-14',
            'status':Attendance.StatusChoice.ABSENT
        }

        response = self.client.post(reverse('attendance-list'), data=data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(Attendance.objects.filter(student=self.student2.pk, date='2026-09-14').exists())

    @patch('apps.attendance.views.send_attendance_sms.delay')
    def test_absent_triggers_sms_task(self, mock_task):
        self.client.force_authenticate(user=self.admin)

        data = {
            'student':self.student2.pk, 'group':self.group2.pk, 'date':'2026-09-21',
            'status':Attendance.StatusChoice.ABSENT
        }

        response = self.client.post(reverse('attendance-list'), data=data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        mock_task.assert_called_once()

    @patch('apps.attendance.views.send_attendance_sms.delay')
    def test_present_does_not_trigger_sms(self, mock_task):
        self.client.force_authenticate(user=self.admin)

        data = {
            'student':self.student.pk, 'group':self.group.pk, 'date':'2026-09-20',
            'status':Attendance.StatusChoice.PRESENT
        }

        response = self.client.post(reverse('attendance-list'), data=data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        mock_task.assert_not_called()

    def test_student_can_list_own_attendance(self):
        self.client.force_authenticate(user=self.student_user)

        response = self.client.get(reverse('attendance-list'), format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)    

    def test_student_cannot_post_attendance(self):
        self.client.force_authenticate(user=self.student_user)

        data = {
            'student':self.student.pk, 'group':self.group.pk, 'date':'2026-09-19',
            'status':Attendance.StatusChoice.PRESENT
        }

        response = self.client.post(reverse('attendance-list'), data=data, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(Attendance.objects.filter(student=self.student.pk, date='2026-09-19').exists())

    def test_admin_can_edit_attendance(self):
        self.client.force_authenticate(user=self.admin)

        data = {
            'status':Attendance.StatusChoice.LATE
        }

        response = self.client.patch(reverse('attendance-detail', kwargs={'pk':self.attendance.pk}), data=data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(Attendance.objects.filter(pk=self.attendance.pk, status=Attendance.StatusChoice.LATE).exists())

    def test_group_teacher_can_edit_attendance(self):
        self.client.force_authenticate(user=self.teacher_user)

        data = {
            'date':'2026-09-18'
        }    

        response = self.client.patch(reverse('attendance-detail', kwargs={'pk':self.attendance.pk}), data=data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(Attendance.objects.filter(pk=self.attendance.pk, date='2026-09-18').exists())

            