from core.views import BaseViewSet
from rest_framework.exceptions import ValidationError
from .serializers import PaymentSerializer
from .models import Payments
from core.permissions import IsAdmin, IsPaymentOwnerOrAdmin

from django.contrib.auth import get_user_model

User = get_user_model()


class PaymentsView(BaseViewSet):
    queryset = Payments.objects.all()
    serializer_class = PaymentSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdmin()]
        else:
            return [IsPaymentOwnerOrAdmin()]

    def get_queryset(self):
        if self.request.user.role == User.Role.ADMIN:
            return Payments.objects.all()
        elif self.request.user.role == User.Role.STUDENT:
            return Payments.objects.filter(student__user=self.request.user)

        return Payments.objects.none()     