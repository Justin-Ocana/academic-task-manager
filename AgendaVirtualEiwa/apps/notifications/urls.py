from django.urls import path
from . import views

urlpatterns = [
    path('test/', views.test_notifications, name='test_notifications'),
    path('mobile-test/', views.mobile_test, name='mobile_test'),
    path('api/get/', views.get_notifications, name='get_notifications'),
    path('api/pending/', views.get_pending_tasks, name='get_pending_tasks'),
    path('api/<int:notification_id>/read/', views.mark_as_read, name='mark_notification_read'),
    path('api/<int:notification_id>/seen/', views.mark_as_seen, name='mark_notification_seen'),
    path('api/<int:notification_id>/delete/', views.delete_notification, name='delete_notification'),
    path('api/read-all/', views.mark_all_as_read, name='mark_all_read'),
    path('api/seen-all/', views.mark_all_as_seen, name='mark_all_seen'),
]
