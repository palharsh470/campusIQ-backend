from rest_framework.routers import DefaultRouter
from .views import DoubtViewSet

router = DefaultRouter()
router.register('doubts', DoubtViewSet, basename='doubt')

urlpatterns = router.urls