from django.db import models
from django.conf import settings

class Teacher(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    subject = models.CharField(max_length=100)
    experience = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
