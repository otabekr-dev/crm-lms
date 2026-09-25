from core.views import BaseViewSet
from rest_framework.generics import CreateAPIView
from .models import Teacher
from .serializers import TeacherSerializer, TeacherRegisterSerializer
from core.permissions import IsAdmin, IsSelfTeacherOrAdmin
from django.core.cache import cache
from rest_framework.response import Response
from django.contrib.auth import get_user_model

User = get_user_model()

class TeacherView(BaseViewSet):
    queryset = Teacher.objects.all()
    serializer_class = TeacherSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [IsAdmin()]
        return [IsSelfTeacherOrAdmin()]

    def get_queryset(self):
        if self.request.user.role == User.Role.ADMIN:
            return Teacher.objects.all()
        elif self.request.user.role == User.Role.TEACHER:
            return Teacher.objects.filter(user=self.request.user)

        return Teacher.objects.none()

    def get_cache_key(self, request):
        model_name = self.queryset.model.__name__
        user_id = request.user.id
        query_params = str(sorted(request.query_params.items()))

        return f'{model_name}{user_id}_{query_params}'    

    def invalidate_cache(self):
        model_name = self.queryset.model.__name__
        pattern = f'{model_name}*'
        cache.delete_pattern(pattern)


    def list(self, request, *args, **kwargs):
        key = self.get_cache_key(request)
        cached_key = cache.get(key)
        if cached_key is not None:
            return Response(cached_key)

        response = super().list(request, *args, **kwargs)
        cache.set(key, response.data, timeout=300)

        return response

    def perform_create(self, serializer):
        super().perform_create(serializer)
        self.invalidate_cache()

    def perform_update(self, serializer):
        super().perform_update(serializer)    
        self.invalidate_cache()

    def perform_destroy(self, instance):
        super().perform_destroy(instance)
        self.invalidate_cache()
    
class TeacherRegisterView(CreateAPIView):
    serializer_class = TeacherRegisterSerializer
    permission_classes = [IsAdmin]

    def perform_create(self, serializer):
        super().perform_create(serializer)
        cache.delete_pattern('Teacher*')