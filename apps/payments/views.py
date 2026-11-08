from core.views import BaseViewSet
from .serializers import PaymentSerializer
from .models import Payments
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.decorators import action
from core.permissions import IsAdmin, IsPaymentOwnerOrAdmin
from django.db.models import Sum, Q, F, DecimalField
from django.db.models.functions import Coalesce
from django.contrib.auth import get_user_model
from datetime import datetime
from apps.students.models import Student
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, OpenApiParameter
from django.db import transaction
from rest_framework.exceptions import ValidationError

User = get_user_model()


def calculate_payment_limit(student, month, amount, payment_id:int|None=None):
    '''This function will work only with transaction atomic'''
    locked_student = Student.objects.select_for_update().get(pk=student.pk)
    payments = Payments.objects.filter(student=locked_student, month=month)

    if payment_id is not None:
        payments = payments.exclude(pk=payment_id)

    students_payment = payments.aggregate(
        student_paid_amount=Coalesce(
            Sum('amount'), 0, output_field=DecimalField()
        )
    )

    paid = students_payment['student_paid_amount']
    group_monthly_fee = locked_student.group.monthly_fee

    if paid + amount > group_monthly_fee:
        remaining = group_monthly_fee - paid
        raise ValidationError(
            f'Limitdan oshib ketdi. Bu oy uchun qolgan summa {remaining}'
        )



class PaymentsView(BaseViewSet):
    queryset = Payments.objects.all()
    serializer_class = PaymentSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['student', 'month', 'student__group']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy', 'debtors']:
            return [IsAdmin()]
        else:
            return [IsPaymentOwnerOrAdmin()]

    def get_queryset(self):
        if self.request.user.role == User.Role.ADMIN:
            return Payments.objects.all()
        elif self.request.user.role == User.Role.STUDENT:
            return Payments.objects.filter(student__user=self.request.user)

        return Payments.objects.none()     

    def perform_create(self, serializer):
        student = serializer.validated_data['student']
        month = serializer.validated_data['month']
        amount = serializer.validated_data['amount']

        with transaction.atomic():
            calculate_payment_limit(student=student, month=month, amount=amount)

            serializer.save()
            
    def perform_update(self, serializer):
        instance = serializer.instance
                
        student = serializer.validated_data.get('student', instance.student)
        month = serializer.validated_data.get('month', instance.month)
        amount = serializer.validated_data.get('amount', instance.amount)
        payment_id = instance.pk        

        with transaction.atomic():
            calculate_payment_limit(student=student, month=month, amount=amount ,payment_id=payment_id)

            serializer.save()

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='month',
                type=str,
                location=OpenApiParameter.QUERY,
                required=False,
                description='YYYY-MM formatda, masalan 2026-10'
            )
        ]
    )
    @action(detail=False, methods=['get'])
    def debtors(self, request:Request) -> Response:
        month_str = request.query_params.get('month')
    
        month = datetime.strptime(month_str, '%Y-%m').date()

        paid_sum = Sum('payments__amount', filter=Q(payments__month=month))

        students = Student.objects.annotate(paid=Coalesce(paid_sum, 0, output_field=DecimalField()))

        students = students.annotate(debt=F('group__monthly_fee') - F('paid'))

        students = students.filter(debt__gt=0)

        return Response(list(students.values('id', 'debt', 'paid')))