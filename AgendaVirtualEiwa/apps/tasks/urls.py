from django.urls import path
from . import views
from . import views_attachments

urlpatterns = [
    path('', views.task_list, name='task_list'),
    path('group/<int:group_id>/', views.group_tasks, name='group_tasks'),
    path('group/<int:group_id>/create/', views.create_task, name='create_task'),
    path('<int:task_id>/toggle/', views.toggle_task_status, name='toggle_task_status'),
    path('<int:task_id>/', views.task_detail, name='task_detail'),
    path('<int:task_id>/edit/', views.edit_task, name='edit_task'),
    path('<int:task_id>/delete/', views.delete_task, name='delete_task'),
    # Solicitudes
    path('request/<int:request_id>/approve/', views.approve_task_request, name='approve_task_request'),
    path('request/<int:request_id>/reject/', views.reject_task_request, name='reject_task_request'),
    path('edit-request/<int:request_id>/approve/', views.approve_edit_request, name='approve_edit_request'),
    path('edit-request/<int:request_id>/reject/', views.reject_edit_request, name='reject_edit_request'),
    # Documentos adjuntos
    path('<int:task_id>/upload-attachment/', views_attachments.upload_attachment, name='upload_attachment'),
    path('attachment/<int:attachment_id>/download/', views_attachments.download_attachment, name='download_attachment'),
    path('attachment/<int:attachment_id>/delete/', views_attachments.delete_attachment, name='delete_attachment'),
    path('attachment/<int:attachment_id>/approve/', views_attachments.approve_attachment, name='approve_attachment'),
    path('attachment/<int:attachment_id>/reject/', views_attachments.reject_attachment, name='reject_attachment'),
]
