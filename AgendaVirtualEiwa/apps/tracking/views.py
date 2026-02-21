from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from apps.groups.models import Group, GroupMember
from apps.tasks.models import Task
from .models import TaskHistory, GroupActivity, RevertibleAction
from .utils import get_group_activity, get_revertible_actions, revert_action


@login_required
def group_history(request, group_id):
    """Ver historial completo de un grupo"""
    group = get_object_or_404(Group, id=group_id)
    
    # Verificar que el usuario es miembro
    try:
        membership = GroupMember.objects.get(group=group, user=request.user)
        is_leader = membership.role == 'leader'
    except GroupMember.DoesNotExist:
        return redirect('dashboard')
    
    # Obtener actividad del grupo
    activity = get_group_activity(group, limit=50)
    
    # Obtener historial de tareas del grupo
    task_history = TaskHistory.objects.filter(group=group).select_related('user', 'task')[:50]
    
    # Combinar y ordenar por fecha
    all_events = []
    
    for act in activity:
        all_events.append({
            'type': 'group',
            'timestamp': act.timestamp,
            'action': act.get_action_display(),
            'user': act.user,
            'affected_user': act.affected_user,
            'description': act.description,
            'details': act.details,
        })
    
    # Agrupar historial por timestamp para encontrar acciones revertibles
    from collections import defaultdict
    from .models import RevertibleAction
    
    history_by_time = defaultdict(list)
    for hist in task_history:
        # Agrupar por timestamp redondeado a minuto
        time_key = hist.timestamp.replace(second=0, microsecond=0)
        history_by_time[time_key].append(hist)
    
    # Obtener todas las acciones revertibles de edición activas
    revertible_edits = {}
    if task_history:
        revertibles = RevertibleAction.objects.filter(
            action_type='task_edit',
            group=group,
            status='active'
        ).select_related('task')
        
        for rev in revertibles:
            # Usar timestamp redondeado como clave
            time_key = rev.timestamp.replace(second=0, microsecond=0)
            if rev.task_id:
                revertible_edits[(time_key, rev.task_id, rev.performed_by_id)] = rev
    
    for hist in task_history:
        # Buscar acción revertible correspondiente
        revertible = None
        if hist.action == 'edited' and hist.task:
            time_key = hist.timestamp.replace(second=0, microsecond=0)
            revertible = revertible_edits.get((time_key, hist.task.id, hist.user.id))
        
        all_events.append({
            'type': 'task',
            'timestamp': hist.timestamp,
            'action': hist.get_action_display(),
            'user': hist.user,
            'task_title': hist.task_title,
            'task': hist.task,
            'field_changed': hist.field_changed,
            'old_value': hist.old_value,
            'new_value': hist.new_value,
            'revertible_action': revertible,
        })
    
    # Ordenar por fecha descendente
    all_events.sort(key=lambda x: x['timestamp'], reverse=True)
    
    # Acciones revertibles (para líderes y creadores según configuración)
    revertible_actions = []
    can_revert = is_leader or group.task_revert_permission == 'leader_creator'
    if can_revert:
        if is_leader:
            # Líder puede ver todas las acciones revertibles
            revertible_actions = get_revertible_actions(group, status='active')
        else:
            # Creador solo puede ver acciones de sus propias tareas
            revertible_actions = RevertibleAction.objects.filter(
                group=group,
                status='active',
                task__created_by=request.user
            ).select_related('performed_by', 'task').order_by('-timestamp')
    
    context = {
        'group': group,
        'is_leader': is_leader,
        'can_revert': can_revert,
        'all_events': all_events[:50],  # Limitar a 50 eventos
        'revertible_actions': revertible_actions,
    }
    
    return render(request, 'tracking/group_history.html', context)


@login_required
def task_history(request, task_id):
    """Ver historial de una tarea específica"""
    task = get_object_or_404(Task, id=task_id)
    
    # Verificar que el usuario es miembro del grupo
    try:
        membership = GroupMember.objects.get(group=task.group, user=request.user)
        is_leader = membership.role == 'leader'
    except GroupMember.DoesNotExist:
        return redirect('dashboard')
    
    # Obtener historial de la tarea
    history = TaskHistory.objects.filter(task=task).select_related('user')
    
    context = {
        'task': task,
        'group': task.group,
        'is_leader': is_leader,
        'history': history,
    }
    
    return render(request, 'tracking/task_history.html', context)


@login_required
def revert_action_view(request, action_id):
    """Revertir una acción (líderes y creadores según configuración)"""
    revertible = get_object_or_404(RevertibleAction, id=action_id)
    
    # Verificar permisos
    try:
        membership = GroupMember.objects.get(group=revertible.group, user=request.user)
        is_leader = membership.role == 'leader'
    except GroupMember.DoesNotExist:
        return redirect('group_history', group_id=revertible.group.id)
    
    # Verificar si puede revertir
    is_creator = revertible.task and revertible.task.created_by == request.user
    can_revert = is_leader or (is_creator and revertible.group.task_revert_permission == 'leader_creator')
    
    if not can_revert:
        from django.contrib import messages
        messages.error(request, 'No tienes permisos para revertir esta acción')
        return redirect('group_history', group_id=revertible.group.id)
    
    if request.method == 'POST':
        success = revert_action(revertible, request.user)
        
        if success:
            # Redirigir al historial con mensaje de éxito
            from django.contrib import messages
            messages.success(request, 'Acción revertida exitosamente')
            return redirect('group_history', group_id=revertible.group.id)
        else:
            from django.contrib import messages
            messages.error(request, 'No se pudo revertir la acción')
            return redirect('group_history', group_id=revertible.group.id)
    
    # Mostrar página de confirmación con detalles de lo que se va a revertir
    context = {
        'revertible': revertible,
        'group': revertible.group,
        'is_leader': True,
    }
    
    return render(request, 'tracking/confirm_revert.html', context)


@login_required
def activity_feed(request, group_id):
    """Feed de actividad reciente del grupo (para AJAX)"""
    group = get_object_or_404(Group, id=group_id)
    
    # Verificar que el usuario es miembro
    try:
        GroupMember.objects.get(group=group, user=request.user)
    except GroupMember.DoesNotExist:
        return JsonResponse({'error': 'No autorizado'}, status=403)
    
    # Obtener actividad reciente
    activity = get_group_activity(group, limit=10)
    
    events = []
    for act in activity:
        events.append({
            'action': act.get_action_display(),
            'user': act.user.nombre if act.user else 'Sistema',
            'timestamp': act.timestamp.isoformat(),
            'description': act.description,
        })
    
    return JsonResponse({'events': events})
