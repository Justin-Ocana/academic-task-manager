from django.urls import path
from . import views

urlpatterns = [
    path('', views.subject_list, name='subject_list'),
    path('group/<int:group_id>/', views.group_subjects, name='group_subjects'),
    path('group/<int:group_id>/add/', views.add_subject, name='add_subject'),
    path('request/<int:request_id>/approve/', views.approve_subject_request, name='approve_subject_request'),
    path('request/<int:request_id>/reject/', views.reject_subject_request, name='reject_subject_request'),
    path('<int:subject_id>/delete/', views.delete_subject, name='delete_subject'),
]
