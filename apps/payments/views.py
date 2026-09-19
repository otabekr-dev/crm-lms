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

User = get_user_model()


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

    @action(detail=False, methods=['get'])
    def debtors(self, request:Request) -> Response:
        month_str = request.query_params.get('month')
    
        month = datetime.strptime(month_str, '%Y-%m').date()

        paid_sum = Sum('payments__amount', filter=Q(payments__month=month))

        students = Student.objects.annotate(paid=Coalesce(paid_sum, 0, output_field=DecimalField()))

        students = students.annotate(debt=F('group__monthly_fee') - F('paid'))

        students = students.filter(debt__gt=0)

        return Response(list(students.values('id', 'debt', 'paid')))