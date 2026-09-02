from rest_framework.viewsets import ModelViewSet
from .models import Student, Group
from .serializers import GroupSerializer, StudentSerializer
from core.permissions import IsAdmin, IsSelfStudentOrAdmin, IsGroupMemberOrAdmin
from django.contrib.auth import get_user_model

User = get_user_model()

class StudentView(ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [IsAdmin()]
        return [IsSelfStudentOrAdmin()]

    def get_queryset(self):
        if self.request.user.role == User.Role.ADMIN:
            return Student.objects.all()
        elif self.request.user.role == User.Role.STUDENT:
            return Student.objects.filter(user=self.request.user)
        elif self.request.user.role == User.Role.TEACHER:
            return Student.objects.filter(group__teacher__user=self.request.user)

        return Student.objects.none()


class GroupView(ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [IsAdmin()]
        return [IsGroupMemberOrAdmin()]


    def get_queryset(self):
        if self.request.user.role == User.Role.ADMIN:
            return Group.objects.all()
        elif self.request.user.role == User.Role.TEACHER:
            return Group.objects.filter(teacher__user=self.request.user)
        elif self.request.user.role == User.Role.STUDENT:
            return Group.objects.filter(student__user=self.request.user)

        return Group.objects.none()