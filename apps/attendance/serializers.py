from rest_framework import serializers
from .models import Attendance
from datetime import date, timedelta

class AttendanceSerializer(serializers.ModelSerializer):

    class Meta:
        model = Attendance
        fields = [
            'id', 'student', 'group',
            'date', 'status', 'created_at'
        ]
        read_only_fields = ['id','created_at']


    def validate_date(self, value):
        if value > date.today():
            raise serializers.ValidationError("Kelajakdagi sanani ishlata olmaysiz")
        if value < date.today() - timedelta(days=7):
            raise serializers.ValidationError("Juda eski sana")
        return value

    def validate(self, attrs):
        if self.instance and 'status' in attrs:
            if attrs['status'] == self.instance.status:
                raise serializers.ValidationError('Status allaqachon shunday, o\'zgartirish shart emas')

        return attrs