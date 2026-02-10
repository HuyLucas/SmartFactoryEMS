from rest_framework.permissions import BasePermission


class IsInGroup(BasePermission):
    required_groups = []

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.is_superuser:
            return True
        return request.user.groups.filter(name__in=self.required_groups).exists()


class IsAdminOrEngineer(IsInGroup):
    required_groups = ['Admin', 'Engineer']
