from rest_framework import permissions


class IsAdminRole(permissions.BasePermission):
    """
    Custom permission class to check if user is authenticated and has admin role.
    
    Usage:
    - Add to view permission_classes: [IsAdminRole]
    - Returns True only if request.user.is_authenticated AND request.user.role == 'admin'
    """
    
    def has_permission(self, request, view):
        """
        Check if user has admin role.
        """
        # First check if user is authenticated
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Then check if user has admin role
        return request.user.role == 'admin'
    
    def has_object_permission(self, request, view, obj):
        """
        Check if user has admin role for object-level permissions.
        """
        return self.has_permission(request, view)


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Custom permission class to check if user is the owner of the object or has admin role.
    Useful for user-specific resources like profiles.
    """
    
    def has_object_permission(self, request, view, obj):
        """
        Check if user is the owner of the object or has admin role.
        """
        # Allow access if user is admin
        if request.user.is_authenticated and request.user.role == 'admin':
            return True
        
        # Allow access if user is the owner
        # Assumes the object has a 'user' field or the object itself is the user
        if hasattr(obj, 'user'):
            return obj.user == request.user
        elif hasattr(obj, 'id'):
            return obj.id == request.user.id
        
        return False
