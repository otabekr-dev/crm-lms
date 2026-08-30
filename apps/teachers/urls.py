from rest_framework.routers import DefaultRouter
from .views import TeacherView

router = DefaultRouter()
router.register('teachers', TeacherView, basename='teacher')

urlpatterns = router.urls
