from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from .permissions import IsAdminRole


@api_view(['GET'])
@permission_classes([IsAdminRole])
def admin_only_view(request):
    """
    Test view that requires admin role.
    Only users with role='admin' can access this endpoint.
    """
    return Response({
        'message': 'Access granted! You have admin privileges.',
        'user': {
            'id': request.user.id,
            'email': request.user.email,
            'role': request.user.role
        }
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def public_view(request):
    """
    Public test view accessible to anyone.
    """
    return Response({
        'message': 'This is a public endpoint.',
        'user_authenticated': request.user.is_authenticated
    }, status=status.HTTP_200_OK)
