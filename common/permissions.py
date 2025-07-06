from rest_framework import permissions

class IsStaffOrReadOnly(permissions.BasePermission):
    """
    Allow read-only access to all, but write access to staff users only.
    """

    def has_permission(self, request, view):
        # SAFE_METHODS = GET, HEAD, OPTIONS
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_staff
