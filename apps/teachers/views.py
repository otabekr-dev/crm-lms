from rest_framework.viewsets import ModelViewSet
from .models import Teacher
from .serializers import TeacherSerializer
from core.permissions import IsAdmin, IsSelfTeacherOrAdmin


class TeacherView(ModelViewSet):
    queryset = Teacher.objects.all()
    serializer_class = TeacherSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [IsAdmin()]
        return [IsSelfTeacherOrAdmin()]
    

    