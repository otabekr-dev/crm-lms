from rest_framework.routers import DefaultRouter
from .views import TeacherView, TeacherRegisterView
from django.urls import path

router = DefaultRouter()
router.register('teachers', TeacherView, basename='teacher')

urlpatterns = [
    path('teacher/register/', TeacherRegisterView.as_view(), name='teacher-register')    
] + router.urls

