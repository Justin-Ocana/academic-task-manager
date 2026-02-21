from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.urls import reverse
from apps.groups.models import Group, GroupMember, JoinRequest
from apps.tasks.models import TaskRequest, TaskEditRequest
from apps.subjects.models import SubjectRequest
from apps.notifications.utils import create_notification


@login_required
def requests_list(request):
    """Lista de grupos con solicitudes pendientes"""
    user = request.user
    
    # Obtener grupos donde el usuario es líder
    leader_memberships = GroupMember.objects.filter(user=user, role='leader').select_related('group')
    
    # Si no es líder de ningún grupo, mostrar mensaje
    if not leader_memberships.exists():
        context = {
            'groups_with_requests': [],
            'has_groups': False,
            'is_leader_of_any': False,
        }
        return render(request, 'requests/requests_list.html', context)
    
    # Si solo es líder de un grupo, redirigir directamente
    if leader_memberships.count() == 1:
        return redirect('group_requests', group_id=leader_memberships.first().group.id)
    
    # Si es líder de múltiples grupos, mostrar selector
    groups_with_requests = []
    
    for membership in leader_memberships:
        group = membership.group
        
        # Contar solicitudes pendientes
        join_count = JoinRequest.objects.filter(group=group, status='pending').count()
        task_count = TaskRequest.objects.filter(group=group, status='pending').count()
        edit_count = TaskEditRequest.objects.filter(task__group=group, status='pending').count()
        subject_count = SubjectRequest.objects.filter(group=group, status='pending').count()
        
        total = join_count + task_count + edit_count + subject_count
        
        groups_with_requests.append({
            'group': group,
            'is_leader': True,
            'total': total,
            'join_requests': join_count,
            'task_requests': task_count,
            'edit_requests': edit_count,
            'subject_requests': subject_count,
        })
    
    context = {
        'groups_with_requests': groups_with_requests,
        'has_groups': True,
        'is_leader_of_any': True,
    }
    
    return render(request, 'requests/requests_list.html', context)


@login_required
def group_requests(request, group_id):
    """Ver solicitudes de un grupo específico"""
    group = get_object_or_404(Group, id=group_id)
    
    try:
        membership = GroupMember.objects.get(group=group, user=request.user)
        is_leader = membership.role == 'leader'
    except GroupMember.DoesNotExist:
        return redirect('requests_list')
    
    request_type = request.GET.get('type', 'all')
    
    if is_leader:
        # Líderes ven todas las solicitudes
        join_requests = JoinRequest.objects.filter(group=group, status='pending').select_related('user')
        task_requests = TaskRequest.objects.filter(group=group, status='pending').select_related('subject', 'requested_by')
        edit_requests = TaskEditRequest.objects.filter(task__group=group, status='pending').select_related('task', 'task__subject', 'requested_by')
        subject_requests = SubjectRequest.objects.filter(group=group, status='pending').select_related('requested_by')
    else:
        # Usuarios normales ven sus propias solicitudes Y solicitudes de edición de sus tareas (si el permiso lo permite)
        join_requests = JoinRequest.objects.none()
        task_requests = TaskRequest.objects.filter(group=group, requested_by=request.user, status='pending').select_related('subject')
        
        # Solicitudes de edición: las que creó el usuario O las de tareas que él creó (si el permiso es approval_leader_creator)
        from django.db.models import Q
        if group.task_edit_permission == 'approval_leader_creator':
            edit_requests = TaskEditRequest.objects.filter(
                Q(task__group=group, requested_by=request.user) | Q(task__group=group, task__created_by=request.user),
                status='pending'
            ).select_related('task', 'task__subject', 'requested_by').distinct()
        else:
            edit_requests = TaskEditRequest.objects.filter(task__group=group, requested_by=request.user, status='pending').select_related('task', 'task__subject')
        
        subject_requests = SubjectRequest.objects.filter(group=group, requested_by=request.user, status='pending')
    
    total_requests = (join_requests.count() + task_requests.count() + 
                     edit_requests.count() + subject_requests.count())
    
    context = {
        'group': group,
        'is_leader': is_leader,
        'request_type': request_type,
        'total_requests': total_requests,
        'join_requests': join_requests,
        'task_requests': task_requests,
        'edit_requests': edit_requests,
        'subject_requests': subject_requests,
    }
    
    return render(request, 'requests/group_requests.html', context)


@login_required
def approve_request(request, request_id):
    """Aprobar solicitud de ingreso"""
    join_request = get_object_or_404(JoinRequest, id=request_id)
    
    # Verificar que es líder
    try:
        GroupMember.objects.get(group=join_request.group, user=request.user, role='leader')
    except GroupMember.DoesNotExist:
        return redirect('group_requests', group_id=join_request.group.id)
    
    # Aprobar
    join_request.status = 'approved'
    join_request.reviewed_by = request.user
    join_request.reviewed_at = timezone.now()
    join_request.save()
    
    # Agregar al grupo
    GroupMember.objects.create(
        group=join_request.group,
        user=join_request.user,
        role='member'
    )
    
    # Si es el primer grupo del usuario, agregarlo automáticamente a dashboard_groups
    user_groups_count = GroupMember.objects.filter(user=join_request.user).count()
    if user_groups_count == 1:  # Es su primer grupo
        join_request.user.dashboard_groups.add(join_request.group)
    
    # Notificar
    create_notification(
        recipient=join_request.user,
        notification_type='general',
        title='Solicitud aprobada',
        message=f'Tu solicitud para unirte a {join_request.group.name} ha sido aprobada',
        sender=request.user,
        action_url=reverse('group_detail', kwargs={'group_id': join_request.group.id})
    )
    
    return redirect('group_requests', group_id=join_request.group.id)


@login_required
def reject_request(request, request_id):
    """Rechazar solicitud de ingreso"""
    join_request = get_object_or_404(JoinRequest, id=request_id)
    
    # Verificar que es líder
    try:
        GroupMember.objects.get(group=join_request.group, user=request.user, role='leader')
    except GroupMember.DoesNotExist:
        return redirect('group_requests', group_id=join_request.group.id)
    
    # Rechazar
    join_request.status = 'rejected'
    join_request.reviewed_by = request.user
    join_request.reviewed_at = timezone.now()
    join_request.save()
    
    # Notificar
    create_notification(
        recipient=join_request.user,
        notification_type='general',
        title='Solicitud rechazada',
        message=f'Tu solicitud para unirte a {join_request.group.name} ha sido rechazada',
        sender=request.user
    )
    
    return redirect('group_requests', group_id=join_request.group.id)
