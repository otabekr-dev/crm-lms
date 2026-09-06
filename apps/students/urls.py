from rest_framework.routers import DefaultRouter
from .views import StudentView, GroupView, StudentRegisterView
from django.urls import path

router = DefaultRouter()
router.register('students', StudentView, basename='students')
router.register('groups', GroupView, basename='group')

urlpatterns = [
    path('students/register/', StudentRegisterView.as_view(), name='student-register')
] + router.urls

