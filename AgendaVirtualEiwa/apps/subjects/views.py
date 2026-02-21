from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.urls import reverse
from apps.groups.models import Group, GroupMember
from apps.notifications.utils import create_notification, notify_group_leaders
from apps.tracking.utils import log_group_activity
from .models import Subject, SubjectRequest
from .forms import SubjectForm, SubjectRequestForm


@login_required
def subject_list(request):
    """Lista de materias por grupo"""
    # Obtener grupos del usuario
    user_groups = GroupMember.objects.filter(user=request.user).select_related('group')
    
    # Si solo tiene un grupo, redirigir directamente
    if user_groups.count() == 1:
        return redirect('group_subjects', group_id=user_groups.first().group.id)
    
    # Obtener materias por grupo
    groups_with_subjects = []
    for membership in user_groups:
        subjects = Subject.objects.filter(group=membership.group)
        groups_with_subjects.append({
            'group': membership.group,
            'membership': membership,
            'subjects': subjects,
            'subjects_count': subjects.count()
        })
    
    context = {
        'groups_with_subjects': groups_with_subjects
    }
    
    return render(request, 'subjects/subject_list.html', context)


@login_required
def group_subjects(request, group_id):
    """Ver materias de un grupo específico"""
    group = get_object_or_404(Group, id=group_id)
    
    # Verificar que el usuario es miembro
    try:
        membership = GroupMember.objects.get(group=group, user=request.user)
        is_leader = membership.role == 'leader'
    except GroupMember.DoesNotExist:
        return redirect('subject_list')
    
    # Obtener materias
    subjects = Subject.objects.filter(group=group).select_related('created_by')
    
    # Solicitudes pendientes (solo para líderes)
    pending_requests = []
    if is_leader:
        pending_requests = SubjectRequest.objects.filter(
            group=group,
            status='pending'
        ).select_related('requested_by')
    
    # Verificar permisos
    can_add = False
    needs_approval = False
    
    if group.subject_permission == 'all':
        can_add = True
    elif group.subject_permission == 'leader':
        can_add = is_leader
    elif group.subject_permission == 'suggest':
        needs_approval = True
        can_add = True
    
    context = {
        'group': group,
        'subjects': subjects,
        'is_leader': is_leader,
        'can_add': can_add,
        'needs_approval': needs_approval,
        'pending_requests': pending_requests
    }
    
    return render(request, 'subjects/group_subjects.html', context)


@login_required
def add_subject(request, group_id):
    """Agregar materia a un grupo"""
    group = get_object_or_404(Group, id=group_id)
    
    # Verificar que el usuario es miembro
    try:
        membership = GroupMember.objects.get(group=group, user=request.user)
        is_leader = membership.role == 'leader'
    except GroupMember.DoesNotExist:
        return redirect('subject_list')
    
    # Verificar permisos
    if group.subject_permission == 'leader' and not is_leader:
        return redirect('group_subjects', group_id=group_id)
    
    if request.method == 'POST':
        # Si requiere aprobación y no es líder, crear solicitud
        if group.subject_permission == 'suggest' and not is_leader:
            form = SubjectRequestForm(request.POST)
            if form.is_valid():
                subject_request = form.save(commit=False)
                subject_request.group = group
                subject_request.requested_by = request.user
                subject_request.save()
                
                # Notificar a los líderes
                notify_group_leaders(
                    group=group,
                    notification_type='general',
                    title='Nueva solicitud de materia',
                    message=f'{request.user.nombre} quiere agregar la materia "{subject_request.name}"',
                    sender=request.user,
                    action_url=reverse('group_requests', kwargs={'group_id': group.id})
                )
                
                return redirect('group_subjects', group_id=group_id)
        else:
            # Crear materia directamente
            form = SubjectForm(request.POST)
            if form.is_valid():
                subject = form.save(commit=False)
                subject.group = group
                subject.created_by = request.user
                subject.save()
                
                # Registrar en tracking
                log_group_activity(
                    group=group,
                    action='subject_added',
                    user=request.user,
                    description=f'Materia "{subject.name}" agregada al grupo',
                    details={'subject_name': subject.name, 'color': subject.color}
                )
                
                return redirect('group_subjects', group_id=group_id)
    else:
        if group.subject_permission == 'suggest' and not is_leader:
            form = SubjectRequestForm()
        else:
            form = SubjectForm()
    
    context = {
        'group': group,
        'form': form,
        'needs_approval': group.subject_permission == 'suggest' and not is_leader
    }
    
    return render(request, 'subjects/add_subject.html', context)


@login_required
def approve_subject_request(request, request_id):
    """Aprobar solicitud de materia"""
    subject_request = get_object_or_404(SubjectRequest, id=request_id)
    
    # Verificar que es líder del grupo
    try:
        GroupMember.objects.get(group=subject_request.group, user=request.user, role='leader')
    except GroupMember.DoesNotExist:
        return redirect('subject_list')
    
    # Aprobar y crear materia
    subject_request.status = 'approved'
    subject_request.reviewed_by = request.user
    subject_request.reviewed_at = timezone.now()
    subject_request.save()
    
    # Crear la materia
    subject = Subject.objects.create(
        group=subject_request.group,
        name=subject_request.name,
        color=subject_request.color,
        created_by=subject_request.requested_by
    )
    
    # Registrar en tracking
    log_group_activity(
        group=subject_request.group,
        action='subject_added',
        user=request.user,
        affected_user=subject_request.requested_by,
        description=f'Materia "{subject.name}" aprobada y agregada (solicitada por {subject_request.requested_by.nombre})',
        details={'subject_name': subject.name, 'color': subject.color, 'approved': True}
    )
    
    # Notificar al usuario
    create_notification(
        recipient=subject_request.requested_by,
        notification_type='general',
        title='Materia aprobada',
        message=f'Tu solicitud para agregar "{subject_request.name}" ha sido aprobada',
        sender=request.user,
        action_url=reverse('group_subjects', kwargs={'group_id': subject_request.group.id})
    )
    
    return redirect('group_requests', group_id=subject_request.group.id)


@login_required
def reject_subject_request(request, request_id):
    """Rechazar solicitud de materia"""
    subject_request = get_object_or_404(SubjectRequest, id=request_id)
    
    # Verificar que es líder del grupo
    try:
        GroupMember.objects.get(group=subject_request.group, user=request.user, role='leader')
    except GroupMember.DoesNotExist:
        return redirect('subject_list')
    
    # Rechazar
    subject_request.status = 'rejected'
    subject_request.reviewed_by = request.user
    subject_request.reviewed_at = timezone.now()
    subject_request.save()
    
    # Notificar al usuario
    create_notification(
        recipient=subject_request.requested_by,
        notification_type='general',
        title='Materia rechazada',
        message=f'Tu solicitud para agregar "{subject_request.name}" ha sido rechazada',
        sender=request.user
    )
    
    return redirect('group_requests', group_id=subject_request.group.id)


@login_required
def delete_subject(request, subject_id):
    """Eliminar materia"""
    subject = get_object_or_404(Subject, id=subject_id)
    
    # Verificar que es líder del grupo
    try:
        GroupMember.objects.get(group=subject.group, user=request.user, role='leader')
    except GroupMember.DoesNotExist:
        return redirect('subject_list')
    
    group_id = subject.group.id
    subject_name = subject.name
    
    # Registrar en tracking antes de eliminar
    log_group_activity(
        group=subject.group,
        action='subject_removed',
        user=request.user,
        description=f'Materia "{subject_name}" eliminada del grupo',
        details={'subject_name': subject_name, 'color': subject.color}
    )
    
    subject.delete()
    
    return redirect('group_subjects', group_id=group_id)
