from core.views import BaseViewSet
from rest_framework.generics import CreateAPIView
from .models import Teacher
from .serializers import TeacherSerializer, TeacherRegisterSerializer
from core.permissions import IsAdmin, IsSelfTeacherOrAdmin
from django.core.cache import cache
from rest_framework.response import Response


class TeacherView(BaseViewSet):
    queryset = Teacher.objects.all()
    serializer_class = TeacherSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [IsAdmin()]
        return [IsSelfTeacherOrAdmin()]
    

    def list(self, request, *args, **kwargs):
        data = cache.get('teacher_list')
        if data is not None:
            return Response(data)
        
        response=super().list(request, *args, **kwargs)
        cache.set('teacher_list', response.data, timeout=300)
        return response

    def perform_create(self, serializer):
        serializer.save()
        cache.delete('teacher_list')

    def perform_update(self, serializer):
        serializer.save()
        cache.delete('teacher_list')

    def perform_destroy(self, instance):
        instance.delete()
        cache.delete('teacher_list')        

class TeacherRegisterView(CreateAPIView):
    serializer_class = TeacherRegisterSerializer
    permission_classes = [IsAdmin]
