from rest_framework.permissions import BasePermission


class IsOwner(BasePermission):
    """
    Allow access if user is an owner of object
    """
    def has_object_permission(self, request, view, obj):
        return bool(request.user == obj.owner)
