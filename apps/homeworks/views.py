from core.views import BaseViewSet
from .serializers import HomeworkSerializer
from core.permissions import IsHomeworkOwnerOrAdmin, IsHomeworkGroupMemberOrAdmin, IsTeacherOrAdmin
from .models import Homework
from rest_framework.exceptions import ValidationError
from django.contrib.auth import get_user_model
from apps.teachers.models import Teacher

User = get_user_model()

class HomeworkView(BaseViewSet):
    queryset = Homework.objects.all()
    serializer_class = HomeworkSerializer

    def perform_create(self, serializer):
        if self.request.user.role == User.Role.TEACHER:
            teacher = Teacher.objects.get(user=self.request.user)
            serializer.save(teacher=teacher)
        else:
            if not serializer.validated_data.get('teacher'):
                raise ValidationError('Admin uchun bu maydon majburiy iltimos Teacher id sini kiriting')
            serializer.save()


    def get_permissions(self):
        if self.action == 'create':
            return [IsTeacherOrAdmin()]
        if self.action in ['update', 'partial_update', 'destroy']:
            return [IsHomeworkOwnerOrAdmin()]
        else:
            return [IsHomeworkGroupMemberOrAdmin()]

    def get_queryset(self):
        if self.request.user.role == User.Role.ADMIN:
            return Homework.objects.all()
        elif self.request.user.role == User.Role.TEACHER:
            return Homework.objects.filter(teacher__user=self.request.user)
        elif self.request.user.role == User.Role.STUDENT:
            return Homework.objects.filter(group__student__user=self.request.user)    
        return Homework.objects.none()