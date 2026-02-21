from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import FileResponse, HttpResponseForbidden, Http404
from django.utils import timezone
from .models import Task, TaskAttachment
from .forms import TaskAttachmentForm
from apps.groups.models import GroupMember
import os


@login_required
def upload_attachment(request, task_id):
    """Subir un documento adjunto a una tarea"""
    task = get_object_or_404(Task, id=task_id)
    group = task.group
    
    # Verificar que el usuario es miembro del grupo
    try:
        membership = GroupMember.objects.get(group=group, user=request.user)
    except GroupMember.DoesNotExist:
        messages.error(request, 'No tienes acceso a este grupo')
        return redirect('dashboard')
    
    # Verificar que los documentos están habilitados
    if not group.documents_enabled:
        messages.error(request, 'Los documentos no están habilitados en este grupo')
        return redirect('task_detail', task_id=task.id)
    
    # Verificar permisos de subida
    can_upload = False
    requires_approval = False
    
    if group.document_upload_permission == 'all':
        can_upload = True
    elif group.document_upload_permission == 'leader':
        can_upload = membership.role == 'leader'
    elif group.document_upload_permission == 'approval':
        can_upload = True
        requires_approval = True
    
    if not can_upload:
        messages.error(request, 'No tienes permiso para subir documentos en este grupo')
        return redirect('task_detail', task_id=task.id)
    
    if request.method == 'POST':
        form = TaskAttachmentForm(request.POST, request.FILES)
        if form.is_valid():
            attachment = form.save(commit=False)
            attachment.task = task
            attachment.uploaded_by = request.user
            attachment.original_filename = request.FILES['file'].name
            attachment.file_size = request.FILES['file'].size
            attachment.file_type = request.FILES['file'].content_type
            
            # Establecer estado según permisos
            if requires_approval:
                attachment.status = 'pending'
                messages.success(request, 'Documento subido. Pendiente de aprobación del líder')
            else:
                attachment.status = 'approved'
                messages.success(request, 'Documento subido exitosamente')
            
            attachment.save()
            
            # TODO: Crear notificación para el líder si requiere aprobación
            
            return redirect('task_detail', task_id=task.id)
    else:
        form = TaskAttachmentForm()
    
    context = {
        'form': form,
        'task': task,
        'group': group,
        'requires_approval': requires_approval,
    }
    return render(request, 'tasks/upload_attachment.html', context)


@login_required
def download_attachment(request, attachment_id):
    """Descargar un documento adjunto"""
    attachment = get_object_or_404(TaskAttachment, id=attachment_id)
    task = attachment.task
    group = task.group
    
    # Verificar que el usuario es miembro del grupo
    if not GroupMember.objects.filter(group=group, user=request.user).exists():
        return HttpResponseForbidden('No tienes acceso a este documento')
    
    # Verificar que el documento está aprobado (o es el uploader/líder)
    membership = GroupMember.objects.get(group=group, user=request.user)
    is_leader = membership.role == 'leader'
    is_uploader = attachment.uploaded_by == request.user
    
    if attachment.status != 'approved' and not (is_leader or is_uploader):
        return HttpResponseForbidden('Este documento no está disponible')
    
    # Verificar que el archivo no fue eliminado físicamente
    if attachment.file_deleted:
        messages.error(request, 'Este documento ya no está disponible (tarea archivada)')
        return redirect('task_detail', task_id=task.id)
    
    # Verificar que el archivo existe
    if not attachment.file:
        raise Http404('Archivo no encontrado')
    
    try:
        # Servir el archivo
        response = FileResponse(
            attachment.file.open('rb'),
            as_attachment=True,
            filename=attachment.original_filename
        )
        return response
    except FileNotFoundError:
        raise Http404('Archivo no encontrado en el servidor')


@login_required
def delete_attachment(request, attachment_id):
    """Eliminar un documento adjunto"""
    attachment = get_object_or_404(TaskAttachment, id=attachment_id)
    task = attachment.task
    group = task.group
    
    # Verificar que el usuario es miembro del grupo
    try:
        membership = GroupMember.objects.get(group=group, user=request.user)
    except GroupMember.DoesNotExist:
        messages.error(request, 'No tienes acceso a este grupo')
        return redirect('dashboard')
    
    # Solo el uploader o el líder pueden eliminar
    is_leader = membership.role == 'leader'
    is_uploader = attachment.uploaded_by == request.user
    
    if not (is_leader or is_uploader):
        messages.error(request, 'No tienes permiso para eliminar este documento')
        return redirect('task_detail', task_id=task.id)
    
    if request.method == 'POST':
        # Eliminar el archivo físico
        if attachment.file:
            try:
                attachment.file.delete()
            except:
                pass
        
        attachment.delete()
        messages.success(request, 'Documento eliminado exitosamente')
        return redirect('task_detail', task_id=task.id)
    
    context = {
        'attachment': attachment,
        'task': task,
    }
    return render(request, 'tasks/delete_attachment.html', context)


@login_required
def approve_attachment(request, attachment_id):
    """Aprobar un documento pendiente"""
    attachment = get_object_or_404(TaskAttachment, id=attachment_id)
    task = attachment.task
    group = task.group
    
    # Verificar que el usuario es líder del grupo
    try:
        membership = GroupMember.objects.get(group=group, user=request.user)
        if membership.role != 'leader':
            messages.error(request, 'Solo el líder puede aprobar documentos')
            return redirect('task_detail', task_id=task.id)
    except GroupMember.DoesNotExist:
        messages.error(request, 'No tienes acceso a este grupo')
        return redirect('dashboard')
    
    if attachment.status != 'pending':
        messages.warning(request, 'Este documento ya fue revisado')
        return redirect('task_detail', task_id=task.id)
    
    attachment.status = 'approved'
    attachment.reviewed_by = request.user
    attachment.reviewed_at = timezone.now()
    attachment.save()
    
    messages.success(request, f'Documento "{attachment.original_filename}" aprobado')
    
    # TODO: Crear notificación para el uploader
    
    return redirect('task_detail', task_id=task.id)


@login_required
def reject_attachment(request, attachment_id):
    """Rechazar un documento pendiente"""
    attachment = get_object_or_404(TaskAttachment, id=attachment_id)
    task = attachment.task
    group = task.group
    
    # Verificar que el usuario es líder del grupo
    try:
        membership = GroupMember.objects.get(group=group, user=request.user)
        if membership.role != 'leader':
            messages.error(request, 'Solo el líder puede rechazar documentos')
            return redirect('task_detail', task_id=task.id)
    except GroupMember.DoesNotExist:
        messages.error(request, 'No tienes acceso a este grupo')
        return redirect('dashboard')
    
    if attachment.status != 'pending':
        messages.warning(request, 'Este documento ya fue revisado')
        return redirect('task_detail', task_id=task.id)
    
    # Eliminar el archivo físico
    if attachment.file:
        try:
            attachment.file.delete()
        except:
            pass
    
    attachment.status = 'rejected'
    attachment.reviewed_by = request.user
    attachment.reviewed_at = timezone.now()
    attachment.save()
    
    messages.success(request, f'Documento "{attachment.original_filename}" rechazado y eliminado')
    
    # TODO: Crear notificación para el uploader
    
    return redirect('task_detail', task_id=task.id)
