from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.utils import timezone
from django.urls import reverse
from .models import Group, GroupMember, JoinRequest, GroupActivity, BannedUser
from .forms import CreateGroupForm, JoinGroupForm, GroupSettingsForm
from apps.notifications.utils import create_notification, notify_group_leaders
from apps.tracking.utils import log_group_activity, create_revertible_action


@login_required
def create_group(request):
    """Vista para crear un nuevo grupo"""
    # Contar grupos actuales del usuario
    user_groups_count = GroupMember.objects.filter(user=request.user).count()
    
    if request.method == 'POST':
        form = CreateGroupForm(request.POST)
        if form.is_valid():
            group = form.save()
            
            # Crear el miembro líder
            GroupMember.objects.create(
                group=group,
                user=request.user,
                role='leader'
            )
            
            # Si es el primer grupo del usuario, agregarlo automáticamente a dashboard_groups
            user_groups_count = GroupMember.objects.filter(user=request.user).count()
            if user_groups_count == 1:  # Es su primer grupo
                request.user.dashboard_groups.add(group)
            
            # Registrar actividad
            GroupActivity.objects.create(
                group=group,
                activity_type='group_created',
                user=request.user,
                description=f'Grupo "{group.name}" creado'
            )
            
            # Registrar en tracking
            log_group_activity(
                group=group,
                action='group_created',
                user=request.user,
                description=f'Grupo "{group.name}" creado con {group.max_members} miembros máximo'
            )
            
            return redirect('group_detail', group_id=group.id)
    else:
        form = CreateGroupForm()
    
    return render(request, 'groups/create_group.html', {
        'form': form,
        'user_groups_count': user_groups_count
    })


@login_required
def join_group(request):
    """Vista para unirse a un grupo con código"""
    # Contar grupos actuales del usuario
    user_groups_count = GroupMember.objects.filter(user=request.user).count()
    
    if request.method == 'POST':
        form = JoinGroupForm(request.POST)
        if form.is_valid():
            invite_code = form.cleaned_data['invite_code']
            message = form.cleaned_data.get('message', '')
            
            try:
                group = Group.objects.get(invite_code=invite_code, is_invite_active=True)
                
                # Verificar si está baneado
                if BannedUser.objects.filter(group=group, user=request.user).exists():
                    return redirect('join_group')
                
                # Verificar si ya es miembro
                if GroupMember.objects.filter(group=group, user=request.user).exists():
                    return redirect('group_detail', group_id=group.id)
                
                # Verificar límite de miembros
                if group.members.count() >= group.max_members:
                    return redirect('join_group')
                
                # Ingreso libre
                if group.entry_type == 'free':
                    GroupMember.objects.create(
                        group=group,
                        user=request.user,
                        role='member'
                    )
                    
                    # Si es el primer grupo del usuario, agregarlo automáticamente a dashboard_groups
                    user_groups_count = GroupMember.objects.filter(user=request.user).count()
                    if user_groups_count == 1:  # Es su primer grupo
                        request.user.dashboard_groups.add(group)
                    
                    GroupActivity.objects.create(
                        group=group,
                        activity_type='member_joined',
                        user=request.user,
                        description=f'{request.user.nombre} se unió al grupo'
                    )
                    
                    # Registrar en tracking
                    log_group_activity(
                        group=group,
                        action='member_joined',
                        user=request.user,
                        description=f'{request.user.nombre} {request.user.apellido} se unió al grupo'
                    )
                    
                    return redirect('group_detail', group_id=group.id)
                
                # Ingreso con aprobación
                else:
                    # Verificar si ya tiene una solicitud pendiente
                    existing_request = JoinRequest.objects.filter(
                        group=group,
                        user=request.user,
                        status='pending'
                    ).first()
                    
                    if existing_request:
                        return redirect('group_list')
                    
                    # Eliminar solicitudes anteriores (aprobadas/rechazadas)
                    JoinRequest.objects.filter(group=group, user=request.user).delete()
                    
                    # Crear nueva solicitud
                    try:
                        join_request = JoinRequest.objects.create(
                            group=group,
                            user=request.user,
                            message=message
                        )
                        
                        # Notificar a los líderes del grupo
                        notify_group_leaders(
                            group=group,
                            notification_type='join_request',
                            title='Nueva solicitud de ingreso',
                            message=f'{request.user.nombre} {request.user.apellido} quiere unirse a {group.name}',
                            sender=request.user,
                            action_url=reverse('group_detail', kwargs={'group_id': group.id})
                        )
                        
                    except Exception as e:
                        pass
                    
                    return redirect('group_list')
                    
            except Group.DoesNotExist:
                form.add_error('invite_code', 'Código de invitación inválido')
    else:
        form = JoinGroupForm()
    
    return render(request, 'groups/join_group.html', {
        'form': form,
        'user_groups_count': user_groups_count
    })


@login_required
def group_detail(request, group_id):
    """Vista de detalle del grupo"""
    group = get_object_or_404(Group, id=group_id)
    
    # Verificar que el usuario es miembro
    try:
        membership = GroupMember.objects.get(group=group, user=request.user)
        is_member = True
        is_leader = membership.role == 'leader'
    except GroupMember.DoesNotExist:
        return redirect('dashboard')
    
    members = group.members.select_related('user').all()
    members_count = members.count()
    
    # Contar roles
    leaders_count = members.filter(role='leader').count()
    co_leaders_count = members.filter(role='co_leader').count()
    
    # Calcular espacios disponibles
    available_slots = group.max_members - members_count
    
    # Actividad reciente (últimas 5 actividades)
    recent_activities = GroupActivity.objects.filter(group=group).select_related('user')[:5]
    
    # Solicitudes pendientes (solo para líderes)
    pending_requests = []
    banned_users = []
    if is_leader:
        pending_requests = JoinRequest.objects.filter(
            group=group,
            status='pending'
        ).select_related('user')
        banned_users = BannedUser.objects.filter(group=group).select_related('user', 'banned_by')
    
    context = {
        'group': group,
        'members': members,
        'members_count': members_count,
        'leaders_count': leaders_count,
        'co_leaders_count': co_leaders_count,
        'available_slots': available_slots,
        'recent_activities': recent_activities,
        'is_leader': is_leader,
        'membership': membership,
        'pending_requests': pending_requests,
        'banned_users': banned_users,
    }
    
    return render(request, 'groups/group_detail.html', context)


@login_required
def group_list(request):
    """Lista de grupos del usuario"""
    user_groups = GroupMember.objects.filter(user=request.user).select_related('group')
    
    # Solicitudes pendientes
    pending_requests = JoinRequest.objects.filter(
        user=request.user,
        status='pending'
    ).select_related('group')
    
    # Solicitudes pendientes para grupos donde es líder
    leader_groups = GroupMember.objects.filter(
        user=request.user,
        role='leader'
    ).values_list('group_id', flat=True)
    
    pending_approvals = JoinRequest.objects.filter(
        group_id__in=leader_groups,
        status='pending'
    ).select_related('user', 'group')
    
    context = {
        'user_groups': user_groups,
        'pending_requests': pending_requests,
        'pending_approvals': pending_approvals,
        'pending_approvals_count': pending_approvals.count(),
    }
    
    return render(request, 'groups/group_list.html', context)


@login_required
def group_settings(request, group_id):
    """Configuración del grupo (solo líder)"""
    group = get_object_or_404(Group, id=group_id)
    
    # Verificar que es líder
    try:
        membership = GroupMember.objects.get(group=group, user=request.user, role='leader')
    except GroupMember.DoesNotExist:
        return redirect('group_detail', group_id=group_id)
    
    if request.method == 'POST':
        form = GroupSettingsForm(request.POST, instance=group)
        if form.is_valid():
            # Guardar valores anteriores ANTES de guardar el formulario
            old_values = {
                'entry_type': group.entry_type,
                'task_create_permission': group.task_create_permission,
                'task_edit_permission': group.task_edit_permission,
                'task_delete_permission': group.task_delete_permission,
                'subject_permission': group.subject_permission,
            }
            
            # Guardar el formulario
            updated_group = form.save()
            
            GroupActivity.objects.create(
                group=group,
                activity_type='settings_changed',
                user=request.user,
                description='Configuración del grupo actualizada'
            )
            
            # Registrar cambios en tracking
            changes = []
            if old_values['entry_type'] != updated_group.entry_type:
                changes.append(f"Tipo de ingreso: {old_values['entry_type']} → {updated_group.entry_type}")
            if old_values['task_create_permission'] != updated_group.task_create_permission:
                changes.append(f"Crear tareas: {old_values['task_create_permission']} → {updated_group.task_create_permission}")
            if old_values['task_edit_permission'] != updated_group.task_edit_permission:
                changes.append(f"Editar tareas: {old_values['task_edit_permission']} → {updated_group.task_edit_permission}")
            if old_values['task_delete_permission'] != updated_group.task_delete_permission:
                changes.append(f"Eliminar tareas: {old_values['task_delete_permission']} → {updated_group.task_delete_permission}")
            if old_values['subject_permission'] != updated_group.subject_permission:
                changes.append(f"Materias: {old_values['subject_permission']} → {updated_group.subject_permission}")
            
            if changes:
                log_group_activity(
                    group=group,
                    action='permissions_changed',
                    user=request.user,
                    description='Permisos del grupo actualizados: ' + ', '.join(changes),
                    details={'changes': changes}
                )
                
                create_revertible_action(
                    action_type='permission_change',
                    group=group,
                    performed_by=request.user,
                    snapshot_data=old_values
                )
            
            return redirect('group_detail', group_id=group_id)
    else:
        form = GroupSettingsForm(instance=group)
    
    context = {
        'group': group,
        'form': form,
    }
    
    return render(request, 'groups/group_settings.html', context)


@login_required
def regenerate_invite_code(request, group_id):
    """Regenerar código de invitación"""
    group = get_object_or_404(Group, id=group_id)
    
    # Verificar que es líder
    try:
        GroupMember.objects.get(group=group, user=request.user, role='leader')
    except GroupMember.DoesNotExist:
        return redirect('group_detail', group_id=group_id)
    
    old_code = group.invite_code
    group.invite_code = group.generate_invite_code()
    group.save()
    
    GroupActivity.objects.create(
        group=group,
        activity_type='invite_regenerated',
        user=request.user,
        description=f'Código de invitación regenerado (anterior: {old_code})'
    )
    
    return redirect('group_detail', group_id=group_id)



@login_required
def approve_request(request, request_id):
    """Aprobar solicitud de ingreso"""
    join_request = get_object_or_404(JoinRequest, id=request_id)
    
    # Verificar que es líder del grupo
    try:
        GroupMember.objects.get(group=join_request.group, user=request.user, role='leader')
    except GroupMember.DoesNotExist:
        return redirect('group_list')
    
    # Aprobar solicitud
    join_request.status = 'approved'
    join_request.reviewed_by = request.user
    join_request.reviewed_at = timezone.now()
    join_request.save()
    
    # Crear miembro
    GroupMember.objects.create(
        group=join_request.group,
        user=join_request.user,
        role='member'
    )
    
    # Registrar actividad
    GroupActivity.objects.create(
        group=join_request.group,
        activity_type='member_joined',
        user=join_request.user,
        description=f'{join_request.user.nombre} se unió al grupo (aprobado por {request.user.nombre})'
    )
    
    # Registrar en tracking
    log_group_activity(
        group=join_request.group,
        action='member_approved',
        user=request.user,
        affected_user=join_request.user,
        description=f'{join_request.user.nombre} {join_request.user.apellido} fue aprobado para unirse al grupo'
    )
    
    # Notificar al usuario que su solicitud fue aprobada
    create_notification(
        recipient=join_request.user,
        notification_type='request_approved',
        title='Solicitud aprobada',
        message=f'Tu solicitud para unirte a {join_request.group.name} ha sido aprobada',
        sender=request.user,
        action_url=reverse('group_detail', kwargs={'group_id': join_request.group.id}),
        content_object=join_request.group
    )
    
    # Redirigir al detalle del grupo si viene de ahí, sino a la lista
    referer = request.META.get('HTTP_REFERER', '')
    if f'/groups/{join_request.group.id}/' in referer:
        return redirect('group_detail', group_id=join_request.group.id)
    return redirect('group_list')


@login_required
def reject_request(request, request_id):
    """Rechazar solicitud de ingreso"""
    join_request = get_object_or_404(JoinRequest, id=request_id)
    
    # Verificar que es líder del grupo
    try:
        GroupMember.objects.get(group=join_request.group, user=request.user, role='leader')
    except GroupMember.DoesNotExist:
        return redirect('group_list')
    
    # Rechazar solicitud
    join_request.status = 'rejected'
    join_request.reviewed_by = request.user
    join_request.reviewed_at = timezone.now()
    join_request.save()
    
    # Registrar en tracking
    log_group_activity(
        group=join_request.group,
        action='member_rejected',
        user=request.user,
        affected_user=join_request.user,
        description=f'Solicitud de {join_request.user.nombre} {join_request.user.apellido} fue rechazada'
    )
    
    # Notificar al usuario que su solicitud fue rechazada
    create_notification(
        recipient=join_request.user,
        notification_type='request_rejected',
        title='Solicitud rechazada',
        message=f'Tu solicitud para unirte a {join_request.group.name} ha sido rechazada',
        sender=request.user,
        content_object=join_request.group
    )
    
    # Redirigir al detalle del grupo si viene de ahí, sino a la lista
    referer = request.META.get('HTTP_REFERER', '')
    if f'/groups/{join_request.group.id}/' in referer:
        return redirect('group_detail', group_id=join_request.group.id)
    return redirect('group_list')


@login_required
def promote_member(request, member_id):
    """Promover miembro a co-líder"""
    member = get_object_or_404(GroupMember, id=member_id)
    
    # Verificar que es líder del grupo
    try:
        GroupMember.objects.get(group=member.group, user=request.user, role='leader')
    except GroupMember.DoesNotExist:
        return redirect('group_detail', group_id=member.group.id)
    
    # Promover a co-líder
    member.role = 'co_leader'
    member.save()
    
    # Registrar actividad
    GroupActivity.objects.create(
        group=member.group,
        activity_type='role_changed',
        user=request.user,
        description=f'{member.user.nombre} fue promovido a Co-líder'
    )
    
    # Registrar en tracking
    log_group_activity(
        group=member.group,
        action='role_changed',
        user=request.user,
        affected_user=member.user,
        description=f'{member.user.nombre} {member.user.apellido} fue promovido a Co-líder',
        details={'old_role': 'member', 'new_role': 'co_leader'}
    )
    
    # Notificar al usuario
    create_notification(
        recipient=member.user,
        notification_type='member_promoted',
        title='Has sido promovido',
        message=f'Ahora eres Co-líder del grupo {member.group.name}',
        sender=request.user,
        action_url=reverse('group_detail', kwargs={'group_id': member.group.id}),
        content_object=member.group
    )
    
    return redirect('group_detail', group_id=member.group.id)


@login_required
def demote_member(request, member_id):
    """Degradar co-líder a miembro"""
    member = get_object_or_404(GroupMember, id=member_id)
    
    # Verificar que es líder del grupo
    try:
        GroupMember.objects.get(group=member.group, user=request.user, role='leader')
    except GroupMember.DoesNotExist:
        messages.error(request, 'No tienes permisos para realizar esta acción.')
        return redirect('group_detail', group_id=member.group.id)
    
    # Degradar a miembro
    member.role = 'member'
    member.save()
    
    # Registrar actividad
    GroupActivity.objects.create(
        group=member.group,
        activity_type='role_changed',
        user=request.user,
        description=f'{member.user.nombre} fue degradado a Miembro'
    )
    
    # Registrar en tracking
    log_group_activity(
        group=member.group,
        action='role_changed',
        user=request.user,
        affected_user=member.user,
        description=f'{member.user.nombre} {member.user.apellido} fue degradado a Miembro',
        details={'old_role': 'co_leader', 'new_role': 'member'}
    )
    
    # Notificar al usuario
    create_notification(
        recipient=member.user,
        notification_type='member_demoted',
        title='Cambio de rol',
        message=f'Tu rol en {member.group.name} ha cambiado a Miembro',
        sender=request.user,
        action_url=reverse('group_detail', kwargs={'group_id': member.group.id}),
        content_object=member.group
    )
    
    return redirect('group_detail', group_id=member.group.id)


@login_required
def remove_member(request, member_id):
    """Expulsar miembro del grupo (sin baneo)"""
    member = get_object_or_404(GroupMember, id=member_id)
    
    # Verificar que es líder del grupo
    try:
        GroupMember.objects.get(group=member.group, user=request.user, role='leader')
    except GroupMember.DoesNotExist:
        messages.error(request, 'No tienes permisos para realizar esta acción.')
        return redirect('group_detail', group_id=member.group.id)
    
    # No permitir expulsar al líder
    if member.role == 'leader':
        return redirect('group_detail', group_id=member.group.id)
    
    group = member.group
    user_to_remove = member.user
    user_name = user_to_remove.nombre
    
    # Notificar al usuario antes de eliminar
    create_notification(
        recipient=user_to_remove,
        notification_type='member_removed',
        title='Has sido expulsado',
        message=f'Has sido expulsado del grupo {group.name}',
        sender=request.user,
        content_object=group
    )
    
    # Registrar actividad antes de eliminar
    GroupActivity.objects.create(
        group=group,
        activity_type='member_removed',
        user=request.user,
        description=f'{user_name} fue expulsado del grupo'
    )
    
    # Registrar en tracking y crear acción revertible
    log_group_activity(
        group=group,
        action='member_removed',
        user=request.user,
        affected_user=user_to_remove,
        description=f'{user_name} {user_to_remove.apellido} fue expulsado del grupo'
    )
    
    create_revertible_action(
        action_type='member_remove',
        group=group,
        performed_by=request.user,
        snapshot_data={'user_id': user_to_remove.id, 'role': member.role},
        affected_user=user_to_remove
    )
    
    # Eliminar miembro
    member.delete()
    
    return redirect('group_detail', group_id=group.id)


@login_required
def ban_member(request, member_id):
    """Banear miembro del grupo"""
    member = get_object_or_404(GroupMember, id=member_id)
    
    # Verificar que es líder del grupo
    try:
        GroupMember.objects.get(group=member.group, user=request.user, role='leader')
    except GroupMember.DoesNotExist:
        messages.error(request, 'No tienes permisos para realizar esta acción.')
        return redirect('group_detail', group_id=member.group.id)
    
    # No permitir banear al líder
    if member.role == 'leader':
        return redirect('group_detail', group_id=member.group.id)
    
    group = member.group
    user_to_ban = member.user
    user_name = user_to_ban.nombre
    
    # Notificar al usuario antes de banear
    create_notification(
        recipient=user_to_ban,
        notification_type='member_banned',
        title='Has sido baneado',
        message=f'Has sido baneado del grupo {group.name} y no podrás volver a unirte',
        sender=request.user,
        content_object=group
    )
    
    # Crear registro de baneo
    BannedUser.objects.get_or_create(
        group=group,
        user=user_to_ban,
        defaults={'banned_by': request.user}
    )
    
    # Registrar actividad
    GroupActivity.objects.create(
        group=group,
        activity_type='member_banned',
        user=request.user,
        description=f'{user_name} fue baneado del grupo'
    )
    
    # Registrar en tracking
    log_group_activity(
        group=group,
        action='member_removed',
        user=request.user,
        affected_user=user_to_ban,
        description=f'{user_name} {user_to_ban.apellido} fue baneado del grupo (no podrá volver)',
        details={'banned': True}
    )
    
    # Eliminar miembro
    member.delete()
    
    return redirect('group_detail', group_id=group.id)


@login_required
def unban_user(request, ban_id):
    """Desbanear usuario del grupo"""
    banned = get_object_or_404(BannedUser, id=ban_id)
    
    # Verificar que es líder del grupo
    try:
        GroupMember.objects.get(group=banned.group, user=request.user, role='leader')
    except GroupMember.DoesNotExist:
        return redirect('group_detail', group_id=banned.group.id)
    
    group = banned.group
    user_name = banned.user.nombre
    
    # Registrar actividad
    GroupActivity.objects.create(
        group=group,
        activity_type='member_unbanned',
        user=request.user,
        description=f'{user_name} fue desbaneado del grupo'
    )
    
    # Eliminar baneo
    banned.delete()
    
    return redirect('group_detail', group_id=group.id)



@login_required
@require_POST
def leave_group(request, group_id):
    """Salir de un grupo"""
    try:
        group = get_object_or_404(Group, id=group_id)
        
        try:
            membership = GroupMember.objects.get(group=group, user=request.user)
            
            # Verificar si es el único líder
            if membership.role == 'leader':
                leaders_count = GroupMember.objects.filter(group=group, role='leader').count()
                if leaders_count == 1:
                    # Es el único líder, no puede salir sin transferir liderazgo
                    return JsonResponse({
                        'success': False,
                        'error': 'Eres el único líder. Debes promover a otro miembro antes de salir o eliminar el grupo.'
                    }, status=400)
            
            # Eliminar membresía
            membership.delete()
            
            # Registrar acción
            try:
                from apps.tracking.utils import log_group_action
                log_group_action(
                    group=group,
                    action='member_left',
                    user=request.user,
                    details={'user_left': f"{request.user.nombre} {request.user.apellido}"}
                )
            except Exception as e:
                # Si falla el logging, continuar de todos modos
                print(f"Error al registrar acción: {e}")
            
            return JsonResponse({
                'success': True,
                'message': 'Has salido del grupo exitosamente'
            })
            
        except GroupMember.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'No eres miembro de este grupo'
            }, status=400)
    
    except Exception as e:
        print(f"Error en leave_group: {e}")
        return JsonResponse({
            'success': False,
            'error': f'Error al salir del grupo: {str(e)}'
        }, status=500)


@login_required
@require_POST
def delete_group(request, group_id):
    """Eliminar un grupo (solo líderes)"""
    group = get_object_or_404(Group, id=group_id)
    
    try:
        membership = GroupMember.objects.get(group=group, user=request.user)
        
        # Solo líderes pueden eliminar
        if membership.role != 'leader':
            return JsonResponse({
                'success': False,
                'error': 'Solo los líderes pueden eliminar el grupo'
            }, status=403)
        
        # Guardar nombre para el mensaje
        group_name = group.name
        
        # Eliminar grupo (esto eliminará en cascada miembros, tareas, etc.)
        group.delete()
        
        return JsonResponse({
            'success': True,
            'message': f'El grupo "{group_name}" ha sido eliminado'
        })
        
    except GroupMember.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'No eres miembro de este grupo'
        }, status=400)
