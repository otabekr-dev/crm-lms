from rest_framework import serializers
from .models import Payments
from datetime import date, timedelta

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
        if value < (date.today() - timedelta(days=60)):
            raise serializers.ValidationError("2 oydan ortiq eski sanani kiritib bo'lmaydi")    
        return value