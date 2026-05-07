from django.urls import path
from .views import (
    register_view,
    CustomTokenObtainPairView,
    profile_view,
    logout_view
)
from .test_views import admin_only_view, public_view

app_name = 'users'

urlpatterns = [
    # Authentication endpoints
    path('auth/register/', register_view, name='register'),
    path('auth/login/', CustomTokenObtainPairView.as_view(), name='login'),
    path('auth/logout/', logout_view, name='logout'),
    
    # User profile endpoint
    path('profile/', profile_view, name='profile'),
    
    # Test endpoints for permissions
    path('admin-only/', admin_only_view, name='admin_only'),
    path('public/', public_view, name='public'),
]
