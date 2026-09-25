from core.views import BaseViewSet
from rest_framework.generics import CreateAPIView
from .models import Student, Group
from .serializers import GroupSerializer, StudentSerializer, StudentRegisterSerializer
from core.permissions import IsAdmin, IsSelfStudentOrAdmin, IsGroupMemberOrAdmin, IsStudentViewerOrAdmin
from django.contrib.auth import get_user_model
from rest_framework.response import Response
from django.core.cache import cache

User = get_user_model()

class StudentView(BaseViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [IsAdmin()]
        elif self.action == 'retrieve':
            return [IsStudentViewerOrAdmin()]
        return [IsSelfStudentOrAdmin()]

    def get_queryset(self):
        if self.request.user.role == User.Role.ADMIN:
            return Student.objects.all()
        elif self.request.user.role == User.Role.STUDENT:
            return Student.objects.filter(user=self.request.user)
        elif self.request.user.role == User.Role.TEACHER:
            return Student.objects.filter(group__teacher__user=self.request.user)

        return Student.objects.none()


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

class GroupView(BaseViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
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
        


class StudentRegisterView(CreateAPIView):
    serializer_class = StudentRegisterSerializer
    permission_classes = [IsAdmin]

    def perform_create(self, serializer):
        super().perform_create(serializer)
        cache.delete_pattern('Student*')