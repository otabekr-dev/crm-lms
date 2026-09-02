from rest_framework.permissions import BasePermission
from django.contrib.auth import get_user_model

User = get_user_model()

class IsTeacher(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == User.Role.TEACHER
    
class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == User.Role.ADMIN

class IsStudent(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == User.Role.STUDENT

class IsTeacherOrAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in [User.Role.TEACHER, User.Role.ADMIN]

class IsSelfTeacherOrAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated


    def has_object_permission(self, request, view, obj):
        if request.user.role == User.Role.ADMIN:
            return True

        return obj.user == request.user
    
class IsGroupMemberOrAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.user.role == User.Role.ADMIN:
            return True
        if request.user.role == User.Role.TEACHER:
            return obj.teacher.user == request.user

        return obj.student_set.filter(user=request.user).exists()

class IsSelfStudentOrAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.user.role == User.Role.ADMIN:
            return True

        return obj.user == request.user    


class IsHomeworkOwnerOrAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.user.role == User.Role.ADMIN:
            return True
        return obj.teacher.user == request.user


class IsHomeworkGroupMemberOrAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.user.role == User.Role.ADMIN:
            return True
        if request.user.role == User.Role.TEACHER:
            return obj.teacher.user == request.user

        return obj.group.student_set.filter(user=request.user).exists()

class IsAttendanceViewerOrAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.user.role == User.Role.ADMIN:
            return True
        if request.user.role == User.Role.TEACHER:
            return obj.group.teacher.user == request.user
        
        return obj.student.user == request.user
            