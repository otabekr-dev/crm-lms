from rest_framework import serializers
from .models import Payments
from datetime import date
from dateutil.relativedelta import relativedelta
from django.db.models import Sum

class PaymentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Payments
        fields = ['id', 'student', 'amount', 'month', 'paid_date']
        read_only_fields = ['id', 'paid_date']


    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError('Miqdor manfiy bulishi mumkin emas')        
        return value

    def validate_month(self, value):
        value = value.replace(day=1)
        limit = (date.today() - relativedelta(months=2)).replace(day=1)

        if value < limit:
            raise serializers.ValidationError("2 oydan ortiq eski oyni kiritib bo'lmaydi")

        return value
    

    def validate(self, attrs):
        if self.instance:
            student = attrs.get('student', self.instance.student)
            month = attrs.get('month', self.instance.month)
            amount = attrs.get('amount', self.instance.amount)
        else:    
            student = attrs['student']
            month = attrs['month']
            amount = attrs['amount']

        payments = Payments.objects.filter(student=student, month=month)

        if self.instance:
            payments = payments.exclude(pk=self.instance.pk)

        monthly_payment = payments.aggregate(paid=Sum('amount'))
        student_already_paid = monthly_payment['paid'] or 0

        monthly_fee = student.group.monthly_fee

        if amount + student_already_paid > monthly_fee:
            raise serializers.ValidationError("Bu oy to'lov miqdoridan ko'p to'layabsiz")

        return attrs