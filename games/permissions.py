from rest_framework import permissions


class GameUpdateDestroyPermission(permissions.BasePermission):
    """Only an organizer of a game can edit and delete games"""

    def has_object_permission(self, request, view, obj):

        if request.method in permissions.SAFE_METHODS:
            return True

        if request.user.is_superuser:
            return True

        return request.user == obj.organizer
