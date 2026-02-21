"""
URL configuration for AgendaVirtualEiwa project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from django.conf import settings
from django.conf.urls.static import static
from apps.core.views import index, dashboard, privacy_policy, terms_conditions, changelog
from apps.core.views_requests import requests_list, group_requests, approve_request, reject_request
from apps.core.profile_views import (
    profile_settings, update_profile, change_password, 
    update_preferences, delete_account, notifications_settings, avatar_settings, avatar_settings_category
)
from apps.accounts.views import register, login_view, logout_view

# Solo en desarrollo: vistas de prueba para páginas de error
if settings.DEBUG:
    from apps.core.views_error_test import test_404, test_403, test_500

urlpatterns = [
    path('', index, name='index'),
    path('privacy/', privacy_policy, name='privacy_policy'),
    path('terms/', terms_conditions, name='terms_conditions'),
    path('changelog/', changelog, name='changelog'),
    path('register/', register, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('dashboard/', dashboard, name='dashboard'),
    
    # Configuración de perfil
    path('settings/profile/', profile_settings, name='profile_settings'),
    path('settings/profile/update/', update_profile, name='update_profile'),
    path('settings/password/change/', change_password, name='change_password'),
    path('settings/preferences/update/', update_preferences, name='update_preferences'),
    path('settings/account/delete/', delete_account, name='delete_account'),
    path('settings/notifications/', notifications_settings, name='notifications_settings'),
    path('settings/avatar/', avatar_settings, name='avatar_settings'),
    path('settings/avatar/<str:category>/', avatar_settings_category, name='avatar_settings_category'),
    
    path('requests/', requests_list, name='requests_list'),
    path('requests/group/<int:group_id>/', group_requests, name='group_requests'),
    path('requests/approve/<int:request_id>/', approve_request, name='approve_request'),
    path('requests/reject/<int:request_id>/', reject_request, name='reject_request'),
    path('groups/', include('apps.groups.urls')),
    path('notifications/', include('apps.notifications.urls')),
    path('subjects/', include('apps.subjects.urls')),
    path('tasks/', include('apps.tasks.urls')),
    path('tracking/', include('apps.tracking.urls')),
    path('calendar/', include('apps.calendar_app.urls')),
    path('admin/', admin.site.urls),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    
    # URLs de prueba para páginas de error (solo en desarrollo)
    urlpatterns += [
        path('test-error/404/', test_404, name='test_404'),
        path('test-error/403/', test_403, name='test_403'),
        path('test-error/500/', test_500, name='test_500'),
    ]
