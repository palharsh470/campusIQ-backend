from rest_framework.permissions import BasePermission


class IsTeacherOrReadOnly(BasePermission):

    def has_permission(self, request, view):
      
        if request.method in ["GET", "HEAD", "OPTIONS"]:
            return request.user.is_authenticated

        return (
            request.user.is_authenticated
            and request.user.role == "TEACHER"
        )