from django.db import models
from django.conf import settings
from apps.teachers.models import Teacher
from core.validators import validate_uzb_numbers

class Group(models.Model):
    name = models.CharField(max_length=120)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    monthly_fee = models.DecimalField(max_digits=10, decimal_places=2)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.id}.{self.name}'


class Student(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    parent_phone = models.CharField(
        max_length=13,
        validators=[validate_uzb_numbers]
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['id']
    
    def __str__(self):
        return f'{self.id}.{self.user.username}'