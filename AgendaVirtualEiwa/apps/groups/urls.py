from django.urls import path
from . import views

urlpatterns = [
    path('', views.group_list, name='group_list'),
    path('create/', views.create_group, name='create_group'),
    path('join/', views.join_group, name='join_group'),
    path('<int:group_id>/', views.group_detail, name='group_detail'),
    path('<int:group_id>/settings/', views.group_settings, name='group_settings'),
    path('<int:group_id>/regenerate-code/', views.regenerate_invite_code, name='regenerate_invite_code'),
    path('request/<int:request_id>/approve/', views.approve_request, name='approve_request'),
    path('request/<int:request_id>/reject/', views.reject_request, name='reject_request'),
    path('member/<int:member_id>/promote/', views.promote_member, name='promote_member'),
    path('member/<int:member_id>/demote/', views.demote_member, name='demote_member'),
    path('member/<int:member_id>/remove/', views.remove_member, name='remove_member'),
    path('member/<int:member_id>/ban/', views.ban_member, name='ban_member'),
    path('ban/<int:ban_id>/unban/', views.unban_user, name='unban_user'),
    path('<int:group_id>/leave/', views.leave_group, name='leave_group'),
    path('<int:group_id>/delete/', views.delete_group, name='delete_group'),
]
