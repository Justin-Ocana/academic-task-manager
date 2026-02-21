from django.urls import path
from . import views

urlpatterns = [
    path('group/<int:group_id>/history/', views.group_history, name='group_history'),
    path('task/<int:task_id>/history/', views.task_history, name='task_history'),
    path('revert/<int:action_id>/', views.revert_action_view, name='revert_action'),
    path('group/<int:group_id>/activity-feed/', views.activity_feed, name='activity_feed'),
]
