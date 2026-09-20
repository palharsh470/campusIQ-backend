from rest_framework.permissions import BasePermission  , SAFE_METHODS

class IsDirector(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role == request.user.Role.DIRECTOR
        )
    
class IsTeacher(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role == request.user.Role.TEACHER
        )
    
class IsStudent(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role == request.user.Role.STUDENT
        )


class IsClassParticipant(BasePermission):
    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        if request.user.role == request.user.Role.DIRECTOR:
            return request.method in SAFE_METHODS
        return request.user.role in (request.user.Role.TEACHER, request.user.Role.STUDENT)