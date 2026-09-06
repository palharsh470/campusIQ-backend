from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import RegisterOrgView, MeView, CreateTeacherView, CreateStudentView

urlpatterns = [
    path('org/register/', RegisterOrgView.as_view(), name='register-org'),
    path('teacher/register/', CreateTeacherView.as_view(), name='create-teacher'),
    path('student/register/', CreateStudentView.as_view(), name='create-student'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('me/', MeView.as_view(), name='me'),
]

