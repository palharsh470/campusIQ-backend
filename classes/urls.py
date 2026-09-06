from rest_framework.routers import DefaultRouter
from .views import (
    ProgramViewSet,
    ClassGroupViewSet,
    TeacherAssignmentViewSet,
    EnrollmentViewSet,
)

router = DefaultRouter()
router.register('programs', ProgramViewSet, basename='program')
router.register('class-groups', ClassGroupViewSet, basename='classgroup')
router.register('teacher/assignments', TeacherAssignmentViewSet, basename='teacherassignment')
router.register('enrollments', EnrollmentViewSet, basename='enrollment')

urlpatterns = router.urls