from rest_framework.routers import DefaultRouter
from .views import PaymentsView

router = DefaultRouter()
router.register('payments', PaymentsView, basename='payments')

urlpatterns = router.urls