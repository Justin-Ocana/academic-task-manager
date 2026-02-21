from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from apps.groups.models import Group, GroupMember, JoinRequest
from apps.tasks.models import TaskRequest, TaskEditRequest
from apps.subjects.models import SubjectRequest


@login_required
def requests_list(request):
    """Lista de grupos para ver solicitudes (líderes ven todas, usuarios ven las suyas)"""
    # Obtener todos los grupos del usuario
    user_groups = GroupMember.objects.filter(user=request.user).select_related('group')
    
    # Si solo tiene un grupo, redirigir directamente
    if user_groups.count() == 1:
        return redirect('group_requests', group_id=user_groups.first().group.id)
    
    # Contar solicitudes por grupo
    groups_with_requests = []
    for membership in user_groups:
        group = membership.group
        is_leader = membership.role == 'leader'
        
        if is_leader:
            # Líderes ven todas las solicitudes del grupo
            join_requests_count = JoinRequest.objects.filter(group=group, status='pending').count()
            task_requests_count = TaskRequest.objects.filter(group=group, status='pending').count()
            edit_requests_count = TaskEditRequest.objects.filter(task__group=group, status='pending').count()
            subject_requests_count = SubjectRequest.objects.filter(group=group, status='pending').count()
        else:
            # Usuarios normales ven solo sus solicitudes
            join_requests_count = 0  # Ya son miembros
            task_requests_count = TaskRequest.objects.filter(group=group, requested_by=request.user, status='pending').count()
            edit_requests_count = TaskEditRequest.objects.filter(task__group=group, requested_by=request.user, status='pending').count()
            subject_requests_count = SubjectRequest.objects.filter(group=group, requested_by=request.user, status='pending').count()
        
        total_requests = join_requests_count + task_requests_count + edit_requests_count + subject_requests_count
        
        if total_requests > 0:
            groups_with_requests.append({
                'group': group,
                'is_leader': is_leader,
                'join_requests': join_requests_count,
                'task_requests': task_requests_count,
                'edit_requests': edit_requests_count,
                'subject_requests': subject_requests_count,
                'total': total_requests
            })
    
    context = {
        'groups_with_requests': groups_with_requests,
        'has_groups': user_groups.exists()
    }
    
    return render(request, 'requests/requests_list.html', context)


@login_required
def group_requests(request, group_id):
    """Ver solicitudes de un grupo (líderes ven todas, usuarios ven las suyas)"""
    group = get_object_or_404(Group, id=group_id)
    
    # Verificar que es miembro
    try:
        membership = GroupMember.objects.get(group=group, user=request.user)
        is_leader = membership.role == 'leader'
    except GroupMember.DoesNotExist:
        return redirect('requests_list')
    
    # Obtener tipo de solicitud a mostrar
    request_type = request.GET.get('type', 'all')
    
    if is_leader:
        # Líderes ven todas las solicitudes
        join_requests = JoinRequest.objects.filter(
            group=group,
            status='pending'
        ).select_related('user').order_by('-created_at')
        
        task_requests = TaskRequest.objects.filter(
            group=group,
            status='pending'
        ).select_related('subject', 'requested_by').order_by('-created_at')
        
        edit_requests = TaskEditRequest.objects.filter(
            task__group=group,
            status='pending'
        ).select_related('task', 'task__subject', 'requested_by').order_by('-created_at')
        
        subject_requests = SubjectRequest.objects.filter(
            group=group,
            status='pending'
        ).select_related('requested_by').order_by('-created_at')
    else:
        # Usuarios normales ven solo sus solicitudes
        join_requests = JoinRequest.objects.none()
        
        task_requests = TaskRequest.objects.filter(
            group=group,
            requested_by=request.user,
            status='pending'
        ).select_related('subject').order_by('-created_at')
        
        edit_requests = TaskEditRequest.objects.filter(
            task__group=group,
            requested_by=request.user,
            status='pending'
        ).select_related('task', 'task__subject').order_by('-created_at')
        
        subject_requests = SubjectRequest.objects.filter(
            group=group,
            requested_by=request.user,
            status='pending'
        ).order_by('-created_at')
    
    context = {
        'group': group,
        'is_leader': is_leader,
        'request_type': request_type,
        'join_requests': join_requests,
        'task_requests': task_requests,
        'edit_requests': edit_requests,
        'subject_requests': subject_requests,
        'total_requests': join_requests.count() + task_requests.count() + edit_requests.count() + subject_requests.count()
    }
    
    return render(request, 'requests/group_requests.html', context)
