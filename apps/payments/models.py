from django.db import models
from apps.students.models import Student

class Payments(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    month = models.DateField()
    paid_date = models.DateTimeField(auto_now_add=True)