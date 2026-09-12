from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import RegisterOrgView, MeView, TeacherView, CreateStudentView
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('teachers', TeacherView, basename='teacher')

urlpatterns = [
    path('org/register/', RegisterOrgView.as_view(), name='register-org'),
    path('student/register/', CreateStudentView.as_view(), name='create-student'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('me/', MeView.as_view(), name='me'),
] + router.urls

