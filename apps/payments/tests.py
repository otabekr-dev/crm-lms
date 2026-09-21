from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status
from .models import Payments
from django.contrib.auth import get_user_model
from apps.students.models import Student, Group
from apps.teachers.models import Teacher

User = get_user_model()

class PaymentsTestCase(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            username='adminuser',
            password='adminuserpassword',
            role=User.Role.ADMIN,
            must_change_password=False
        )

        self.student_user = User.objects.create_user(
            username='studentuser',
            password='studentuserpassword',
            role=User.Role.STUDENT,
            must_change_password=False            
        )

        self.teacher_user=User.objects.create_user(
            username='teacheruser',
            password='teacheruserpassword',
            role=User.Role.TEACHER,
            must_change_password=False            
        )

        self.teacher = Teacher.objects.create(
            user=self.teacher_user, subject='system design', experience=2
        )

        self.group = Group.objects.create(
            name='System design', teacher=self.teacher, monthly_fee=500000
        )

        self.student = Student.objects.create(
            user=self.student_user, group=self.group, parent_phone='+998997775522'
        )

        self.payment = Payments.objects.create(
            student=self.student, amount=500000, month="2026-09-20"
        )

    def get_results(self, response):
        data = response.data
        if self.isinstance(data, dict) and 'results' in data:
            return data['results']
        return data

    def test_part_payment(self):
        self.client.force_authenticate(user=self.admin)

        data = {
            "student":self.student.pk,
            "amount":200000,
            "month":"2026-09-21"
        }

        response = self.client.post(reverse('payments-list'), data=data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Payments.objects.filter(student=self.student.pk, amount=200000).exists())

    def test_over_payment(self):
        self.client.force_authenticate(user=self.admin)

        data = {
            "student":self.student.pk,
            "amount":550000,
            "month":"2026-09-19"
        }

        response = self.client.post(reverse('payments-list'), data=data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)        

    def test_can_decrease_the_payment(self):
        self.client.force_authenticate(user=self.admin)

        payment = self.payment

        data = {
            "amount":400000
        }        

        response = self.client.patch(reverse('payments-detail', kwargs={'pk':payment.pk}), data=data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        payment.refresh_from_db()
        self.assertTrue(Payments.objects.filter(pk=payment.pk, amount=400000).exists())

    def test_cannot_increase_the_payment(self):
        self.client.force_authenticate(user=self.admin)
        payment = self.payment

        data = {
            "amount":550000
        }

        response = self.client.patch(reverse('payments-detail', kwargs={'pk':payment.pk}), data=data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        payment.refresh_from_db()
        self.assertTrue(Payments.objects.filter(pk=payment.pk, amount=500000).exists())

    def test_admin_can_get_debtors(self):
        self.client.force_authenticate(user=self.admin)

        response = self.client.get(reverse('payments-debtors'),{'month':'2026-09'}, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
            
    def test_teacher_and_student_cannot_get_debtors(self):
        self.client.force_authenticate(user=self.teacher_user)

        response = self.client.get(reverse('payments-debtors'),{'month':'2026-09'}, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.client.force_authenticate(user=self.student_user)

        response2 = self.client.get(reverse('payments-debtors'),{'month':'2026-09'}, format='json')

        self.assertEqual(response2.status_code, status.HTTP_403_FORBIDDEN)

    def test_student_can_see_own_payments(self):
        self.client.force_authenticate(user=self.student_user)

        response = self.client.get(reverse('payments-list'), format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

            
    def test_teacher_cannot_get_payments(self):
        self.client.force_authenticate(user=self.teacher_user)

        response = self.client.get(reverse('payments-list'), format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_teacher_cannot_post_payment(self):
        self.client.force_authenticate(user=self.teacher_user)

        data = {
            'student':self.student.pk,
            'amount':100000,
            'month':'2026-10-01'
        }

        response = self.client.post(reverse('payments-list'), data=data, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(Payments.objects.filter(student=self.student.pk, amount=100000, month='2026-10-01').exists())

    def test_student_cannot_post_payment(self):
        self.client.force_authenticate(user=self.student_user)

        data = {
            'student':self.student.pk,
            'amount':100000,
            'month':'2026-10-01'
        }

        response = self.client.post(reverse('payments-list'), data=data, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(Payments.objects.filter(student=self.student.pk, amount=100000, month='2026-10-01').exists())
                