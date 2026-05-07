"""
URL configuration for mnm_ck project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static

# Custom error handlers
handler400 = 'eshop.error_views.bad_request'
handler403 = 'eshop.error_views.permission_denied'
handler404 = 'eshop.error_views.page_not_found'
handler500 = 'eshop.error_views.server_error'

urlpatterns = [
    path('', include('eshop.urls'), name='eshop'),
    path('admin/', admin.site.urls),
    # API endpoints
    path('api/', include('users.urls')),
    # Dashboard (includes checkout API at /dashboard/api/checkout/)
    path('dashboard/', include('dashboard.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
