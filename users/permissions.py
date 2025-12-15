from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsModder(BasePermission):
    """Allows access only to users with modder status."""
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.modder_status in ['modder', 'verified'])

class IsOwnerOrReadOnly(BasePermission):
    """Object-level permission to only allow owners of an object to edit it."""
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        # Check if the obj has an 'author' attribute or 'user' attribute
        return obj.author == request.user if hasattr(obj, 'author') else obj.user == request.user