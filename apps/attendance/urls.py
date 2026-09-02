from rest_framework.routers import DefaultRouter
from .views import AttendanceView

router = DefaultRouter()

router.register('attendance', AttendanceView, basename='attendance')

urlpatterns = router.urls
