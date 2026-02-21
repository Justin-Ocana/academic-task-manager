# Utilidades para optimización de consultas a base de datos
from django.db.models import Prefetch, Q
from functools import wraps
from django.core.cache import cache
import hashlib
import json


def cache_query(timeout=300):
    """
    Decorador para cachear resultados de consultas
    
    Uso:
    @cache_query(timeout=600)
    def get_user_groups(user_id):
        return Group.objects.filter(members__user_id=user_id)
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Crear clave única basada en función y argumentos
            cache_key = f"{func.__name__}_{hashlib.md5(str(args).encode() + str(kwargs).encode()).hexdigest()}"
            
            # Intentar obtener del cache
            result = cache.get(cache_key)
            if result is not None:
                return result
            
            # Si no está en cache, ejecutar función
            result = func(*args, **kwargs)
            
            # Guardar en cache
            cache.set(cache_key, result, timeout)
            
            return result
        return wrapper
    return decorator


def optimize_group_query(queryset):
    """
    Optimiza consultas de grupos con select_related y prefetch_related
    """
    return queryset.select_related(
        'created_by'
    ).prefetch_related(
        'members__user',
        'tasks',
        'subjects'
    )


def optimize_task_query(queryset):
    """
    Optimiza consultas de tareas
    """
    return queryset.select_related(
        'group',
        'subject',
        'created_by',
        'assigned_to'
    ).prefetch_related(
        'attachments'
    )


def optimize_notification_query(queryset):
    """
    Optimiza consultas de notificaciones
    """
    return queryset.select_related(
        'user',
        'group',
        'task'
    )


def paginate_queryset(queryset, page=1, per_page=20):
    """
    Paginación eficiente de querysets
    """
    start = (page - 1) * per_page
    end = start + per_page
    return queryset[start:end]


def bulk_create_with_return(model, objects):
    """
    Bulk create que retorna los objetos creados con IDs
    """
    return model.objects.bulk_create(objects, batch_size=100)


def bulk_update_optimized(queryset, field_updates):
    """
    Actualización masiva optimizada
    
    Uso:
    bulk_update_optimized(
        Task.objects.filter(group_id=1),
        {'status': 'completed'}
    )
    """
    return queryset.update(**field_updates)


class QueryOptimizer:
    """
    Clase helper para optimizar consultas comunes
    """
    
    @staticmethod
    def get_user_groups_optimized(user):
        """Obtiene grupos del usuario con datos relacionados"""
        from apps.groups.models import Group
        return optimize_group_query(
            Group.objects.filter(members__user=user)
        ).distinct()
    
    @staticmethod
    def get_group_tasks_optimized(group):
        """Obtiene tareas del grupo optimizadas"""
        return optimize_task_query(
            group.tasks.all()
        )
    
    @staticmethod
    def get_user_notifications_optimized(user, limit=50):
        """Obtiene notificaciones del usuario optimizadas"""
        from apps.notifications.models import Notification
        return optimize_notification_query(
            Notification.objects.filter(user=user)
        ).order_by('-created_at')[:limit]
    
    @staticmethod
    def get_pending_requests_optimized(user):
        """Obtiene solicitudes pendientes optimizadas"""
        from apps.core.models import GroupRequest
        return GroupRequest.objects.filter(
            group__members__user=user,
            group__members__role='leader',
            status='pending'
        ).select_related(
            'user',
            'group'
        ).distinct()


# Funciones de utilidad para vistas
def get_or_none(model, **kwargs):
    """
    Obtiene un objeto o retorna None en lugar de lanzar excepción
    """
    try:
        return model.objects.get(**kwargs)
    except model.DoesNotExist:
        return None


def exists_or_false(queryset):
    """
    Verifica existencia de manera eficiente
    """
    return queryset.exists()
