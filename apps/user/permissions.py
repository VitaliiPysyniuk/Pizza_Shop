from rest_framework.permissions import BasePermission


class IsManager(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return bool(user.is_active and user.role == 'manager')
