from rest_framework.routers import DefaultRouter
from .views import HomeworkView
router = DefaultRouter()

router.register('homework', HomeworkView, basename='homework')

urlpatterns = router.urls
