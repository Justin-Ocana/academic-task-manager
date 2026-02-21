from django.utils import timezone
from .models import TaskHistory, GroupActivity, UserActionLog, RevertibleAction


def log_task_action(task, action, user, field_changed=None, old_value=None, new_value=None, details=None):
    """
    Registrar acción en una tarea
    
    Args:
        task: Instancia de Task (puede ser None si fue eliminada)
        action: 'created', 'edited', 'deleted', 'completed', 'reopened'
        user: Usuario que realizó la acción
        field_changed: Campo que cambió (opcional)
        old_value: Valor anterior (opcional)
        new_value: Valor nuevo (opcional)
        details: Diccionario con detalles adicionales (opcional)
    """
    TaskHistory.objects.create(
        task=task,
        task_title=task.title if task else "Tarea eliminada",
        group=task.group if task else None,
        action=action,
        user=user,
        field_changed=field_changed or '',
        old_value=str(old_value) if old_value else '',
        new_value=str(new_value) if new_value else '',
        details=details or {}
    )


def log_group_activity(group, action, user, affected_user=None, description='', details=None):
    """
    Registrar actividad en un grupo
    
    Args:
        group: Instancia de Group
        action: Tipo de acción (ver GroupActivity.ACTION_CHOICES)
        user: Usuario que realizó la acción
        affected_user: Usuario afectado por la acción (opcional)
        description: Descripción de la acción
        details: Diccionario con detalles adicionales
    """
    GroupActivity.objects.create(
        group=group,
        action=action,
        user=user,
        affected_user=affected_user,
        description=description,
        details=details or {}
    )


def log_user_action(user, action_type, ip_address=None, user_agent=None, group=None, task=None, details=None):
    """
    Registrar acción general de usuario
    
    Args:
        user: Usuario que realizó la acción
        action_type: Tipo de acción (ver UserActionLog.ACTION_TYPES)
        ip_address: IP del usuario (opcional)
        user_agent: User agent del navegador (opcional)
        group: Grupo relacionado (opcional)
        task: Tarea relacionada (opcional)
        details: Diccionario con detalles adicionales
    """
    UserActionLog.objects.create(
        user=user,
        action_type=action_type,
        ip_address=ip_address,
        user_agent=user_agent,
        group=group,
        task=task,
        details=details or {}
    )


def create_revertible_action(action_type, group, performed_by, snapshot_data, task=None, affected_user=None):
    """
    Crear una acción que puede ser revertida
    
    Args:
        action_type: Tipo de acción revertible
        group: Grupo donde ocurrió
        performed_by: Usuario que realizó la acción
        snapshot_data: Diccionario con el estado antes del cambio
        task: Tarea afectada (opcional)
        affected_user: Usuario afectado (opcional)
    
    Returns:
        Instancia de RevertibleAction
    """
    return RevertibleAction.objects.create(
        action_type=action_type,
        group=group,
        performed_by=performed_by,
        snapshot_data=snapshot_data,
        task=task,
        affected_user=affected_user
    )


def revert_action(revertible_action, reverted_by):
    """
    Revertir una acción
    
    Args:
        revertible_action: Instancia de RevertibleAction
        reverted_by: Usuario que revierte la acción
    
    Returns:
        True si se revirtió exitosamente, False en caso contrario
    """
    if revertible_action.status != 'active':
        return False
    
    try:
        snapshot = revertible_action.snapshot_data
        
        if revertible_action.action_type == 'task_edit' and revertible_action.task:
            # Revertir edición de tarea
            task = revertible_action.task
            
            # Restaurar documentos eliminados si los hay (solo si no fueron eliminados permanentemente)
            if 'deleted_attachments' in snapshot and not snapshot.get('deleted_permanently', False):
                from apps.tasks.models import TaskAttachment
                for att_id in snapshot['deleted_attachments']:
                    try:
                        # El documento aún existe en BD, solo estaba marcado para eliminar
                        attachment = TaskAttachment.objects.get(id=att_id)
                        # No hacer nada, el documento se mantiene
                        log_task_action(task, 'document_restored', reverted_by, 'attachment', '', attachment.original_filename)
                    except TaskAttachment.DoesNotExist:
                        pass
            
            # Revertir campos de la tarea
            for field, value in snapshot.items():
                if field not in ['deleted_attachments', 'deleted_permanently']:  # Saltar campos especiales
                    setattr(task, field, value)
            task.save()
            
            log_task_action(
                task=task,
                action='edited',
                user=reverted_by,
                details={'reverted': True, 'original_editor': revertible_action.performed_by.id}
            )
        
        elif revertible_action.action_type == 'task_delete':
            # Restaurar tarea eliminada
            from apps.tasks.models import Task
            Task.objects.create(**snapshot)
            
        elif revertible_action.action_type == 'member_remove' and revertible_action.affected_user:
            # Re-agregar miembro expulsado
            from apps.groups.models import GroupMember
            GroupMember.objects.create(
                group=revertible_action.group,
                user=revertible_action.affected_user,
                role='member'
            )
            
            log_group_activity(
                group=revertible_action.group,
                action='member_approved',
                user=reverted_by,
                affected_user=revertible_action.affected_user,
                description=f'Revertida expulsión de {revertible_action.affected_user.nombre}'
            )
        
        elif revertible_action.action_type == 'permission_change':
            # Revertir cambios de permisos
            group = revertible_action.group
            for field, value in snapshot.items():
                setattr(group, field, value)
            group.save()
            
            log_group_activity(
                group=group,
                action='permissions_changed',
                user=reverted_by,
                description='Permisos revertidos a estado anterior'
            )
        
        # Marcar como revertida
        revertible_action.status = 'reverted'
        revertible_action.reverted_by = reverted_by
        revertible_action.reverted_at = timezone.now()
        revertible_action.save()
        
        return True
        
    except Exception as e:
        print(f"Error al revertir acción: {e}")
        return False


def get_task_history(task, limit=None):
    """Obtener historial de una tarea"""
    history = TaskHistory.objects.filter(task=task)
    if limit:
        history = history[:limit]
    return history


def get_group_activity(group, limit=None):
    """Obtener actividad de un grupo"""
    activity = GroupActivity.objects.filter(group=group).select_related('user', 'affected_user')
    if limit:
        activity = activity[:limit]
    return activity


def get_user_actions(user, limit=None):
    """Obtener acciones de un usuario"""
    actions = UserActionLog.objects.filter(user=user)
    if limit:
        actions = actions[:limit]
    return actions


def get_revertible_actions(group, status='active'):
    """Obtener acciones revertibles de un grupo"""
    return RevertibleAction.objects.filter(
        group=group,
        status=status
    ).select_related('performed_by', 'reverted_by', 'task', 'affected_user')


def get_client_ip(request):
    """Obtener IP del cliente"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def get_user_agent(request):
    """Obtener user agent del navegador"""
    return request.META.get('HTTP_USER_AGENT', '')[:255]
