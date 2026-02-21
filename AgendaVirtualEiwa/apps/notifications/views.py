from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_POST
from .models import Notification


@login_required
def get_notifications(request):
    """Obtener notificaciones del usuario (API)"""
    notifications = Notification.objects.filter(
        recipient=request.user
    )[:20]  # Últimas 20
    
    unread_count = Notification.objects.filter(
        recipient=request.user,
        is_read=False
    ).count()
    
    data = {
        'notifications': [
            {
                'id': n.id,
                'type': n.notification_type,
                'title': n.title,
                'message': n.message,
                'action_url': n.action_url,
                'is_read': n.is_read,
                'is_seen': n.is_seen,
                'created_at': n.created_at.isoformat(),
                'sender': {
                    'nombre': n.sender.nombre if n.sender else None,
                    'apellido': n.sender.apellido if n.sender else None,
                } if n.sender else None
            }
            for n in notifications
        ],
        'unread_count': unread_count
    }
    
    return JsonResponse(data)


@login_required
@require_POST
def mark_as_read(request, notification_id):
    """Marcar notificación como leída"""
    notification = get_object_or_404(Notification, id=notification_id, recipient=request.user)
    notification.is_read = True
    notification.read_at = timezone.now()
    notification.save()
    
    return JsonResponse({'success': True})


@login_required
@require_POST
def mark_as_seen(request, notification_id):
    """Marcar notificación como vista"""
    notification = get_object_or_404(Notification, id=notification_id, recipient=request.user)
    notification.is_seen = True
    notification.save()
    
    return JsonResponse({'success': True})


@login_required
@require_POST
def mark_all_as_read(request):
    """Marcar todas las notificaciones como leídas"""
    Notification.objects.filter(
        recipient=request.user,
        is_read=False
    ).update(is_read=True, read_at=timezone.now())
    
    return JsonResponse({'success': True})


@login_required
@require_POST
def mark_all_as_seen(request):
    """Marcar todas las notificaciones como vistas"""
    Notification.objects.filter(
        recipient=request.user,
        is_seen=False
    ).update(is_seen=True)
    
    return JsonResponse({'success': True})


@login_required
@require_POST
def delete_notification(request, notification_id):
    """Eliminar notificación"""
    notification = get_object_or_404(Notification, id=notification_id, recipient=request.user)
    notification.delete()
    
    return JsonResponse({'success': True})



@login_required
def test_notifications(request):
    """Página de prueba de notificaciones"""
    return render(request, 'notifications/test.html')


def mobile_test(request):
    """Página de prueba para móviles (sin login)"""
    return render(request, 'notifications/mobile-test.html')


@login_required
def get_pending_tasks(request):
    """Obtener tareas pendientes y próximas a vencer para notificaciones push"""
    from apps.tasks.models import Task, TaskCompletion
    from apps.groups.models import GroupMember
    from datetime import timedelta
    
    # Obtener grupos del usuario
    user_group_ids = GroupMember.objects.filter(user=request.user).values_list('group_id', flat=True)
    
    # Fecha y hora actual
    now = timezone.now()
    today = now.date()
    
    # Tareas del usuario
    tasks = Task.objects.filter(
        group_id__in=user_group_ids
    ).select_related('subject', 'group')
    
    # Fechas importantes
    tomorrow = today + timedelta(days=1)
    
    # Listas de tareas
    today_tasks = []
    tomorrow_tasks = []
    due_soon_tasks = []
    overdue_tasks = []
    
    for task in tasks:
        # Verificar si el usuario ya completó la tarea
        completion = TaskCompletion.objects.filter(task=task, user=request.user).first()
        if completion and completion.completed:
            continue
        
        # Calcular horas hasta vencimiento
        task_datetime = timezone.make_aware(
            timezone.datetime.combine(task.due_date, timezone.datetime.min.time())
        )
        hours_left = (task_datetime - now).total_seconds() / 3600
        
        task_data = {
            'id': task.id,
            'title': task.title,
            'subject': task.subject.name,
            'due_date': task.due_date.isoformat(),
            'hours_left': round(hours_left, 1)
        }
        
        # Clasificar tarea
        if task.due_date < today:
            overdue_tasks.append(task_data)
        elif task.due_date == today:
            today_tasks.append(task_data)
        elif task.due_date == tomorrow:
            tomorrow_tasks.append(task_data)
        elif 0 < hours_left <= 24:
            due_soon_tasks.append(task_data)
    
    return JsonResponse({
        'today': today_tasks,
        'tomorrow': tomorrow_tasks,
        'due_soon': due_soon_tasks,
        'overdue': overdue_tasks,
        'count': {
            'today': len(today_tasks),
            'tomorrow': len(tomorrow_tasks),
            'due_soon': len(due_soon_tasks),
            'overdue': len(overdue_tasks)
        }
    })
