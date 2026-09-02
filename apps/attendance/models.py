from django.db import models
from apps.students.models import Student
from apps.students.models import Group

class Attendance(models.Model):
    class StatusChoice(models.TextChoices):
        PRESENT = "PRESENT", "Present"
        ABSENT = "ABSENT", 'Absent'
        LATE = "LATE", "Late"

    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    date = models.DateField()
    status = models.CharField(max_length=25, choices=StatusChoice.choices)
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"{self.id}.{self.student.user.first_name} -> {self.status}"
    