from rest_framework.routers import DefaultRouter
from .views import LecturesViewSet, MaterialViewSet

router = DefaultRouter()
router.register('lectures', LecturesViewSet, basename='program')
router.register('materials', MaterialViewSet, basename='classgroup')


urlpatterns = router.urls