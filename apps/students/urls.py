from rest_framework.routers import DefaultRouter
from .views import StudentView, GroupView

router = DefaultRouter()
router.register('students', StudentView, basename='students')
router.register('groups', GroupView, basename='group')

urlpatterns = router.urls
