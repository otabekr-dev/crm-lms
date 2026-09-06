from core.views import BaseViewSet
from .models import Attendance
from .serializers import AttendanceSerializer
from core.permissions import IsTeacherOrAdmin, IsAttendanceViewerOrAdmin
from django.contrib.auth import get_user_model
from rest_framework.exceptions import ValidationError
from .tasks import send_attendance_sms

User = get_user_model()

class AttendanceView(BaseViewSet):
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [IsTeacherOrAdmin()]
        else:
            return [IsAttendanceViewerOrAdmin()]

    def perform_create(self, serializer):
        if self.request.user.role == User.Role.TEACHER:
            group = serializer.validated_data.get('group')
            if group.teacher.user != self.request.user:
                raise ValidationError('Bu guruh sizga tegishli emas')

        attendance = serializer.save()

        if attendance.status == Attendance.StatusChoice.ABSENT:
            send_attendance_sms.delay(
                attendance.student.parent_phone,
                'Farzandingiz darsga kelmadi'
            )            

    def get_queryset(self):
        if self.request.user.role == User.Role.ADMIN:
            return Attendance.objects.all()
        elif self.request.user.role == User.Role.TEACHER:
            return Attendance.objects.filter(group__teacher__user=self.request.user)
        elif self.request.user.role == User.Role.STUDENT:
            return Attendance.objects.filter(student__user=self.request.user)

        return Attendance.objects.none()
