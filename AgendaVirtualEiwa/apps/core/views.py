
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse


def index(request):
    # Si el usuario está autenticado, redirigir al dashboard
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'Index/index.html')


def privacy_policy(request):
    """Vista para la política de privacidad"""
    return render(request, 'Index/privacy.html')


def terms_conditions(request):
    """Vista para los términos y condiciones"""
    return render(request, 'Index/terms.html')


@login_required
def changelog(request):
    """Vista para el registro de cambios"""
    return render(request, 'changelog.html')


@login_required
def dashboard(request):
    from apps.groups.models import GroupMember, JoinRequest
    from apps.tasks.models import Task
    from django.utils import timezone
    from datetime import timedelta
    from django.db.models import Q, Count
    
    # Verificar si el usuario tiene grupos APROBADOS (es miembro)
    user_groups = GroupMember.objects.filter(user=request.user).select_related('group')
    has_groups = user_groups.exists()
    user_groups_count = user_groups.count()
    
    # Verificar solicitudes pendientes (no cuenta como tener grupo)
    pending_requests = JoinRequest.objects.filter(
        user=request.user, 
        status='pending'
    ).select_related('group')
    
    # Obtener modo multigrupo del usuario
    multigroup_mode = request.user.multigroup_mode
    
    # Determinar qué grupos usar según el modo y configuración de dashboard
    dashboard_groups = request.user.dashboard_groups.all()
    
    if dashboard_groups.exists():
        # Si hay grupos configurados para el dashboard, usar esos
        user_group_ids = list(dashboard_groups.values_list('id', flat=True))
    elif multigroup_mode == 'unified':
        # Modo unificado sin configuración: usar todos los grupos
        user_group_ids = list(user_groups.values_list('group_id', flat=True))
    else:
        # Modo separado: usar solo el grupo activo
        if request.user.last_active_group_id:
            user_group_ids = [request.user.last_active_group_id]
        elif user_groups_count == 1:
            # Si solo tiene un grupo, usarlo automáticamente
            user_group_ids = [user_groups.first().group.id]
        else:
            # Si no hay grupo activo y tiene múltiples grupos, no mostrar datos
            user_group_ids = []
    
    # Importar modelos necesarios
    from apps.tasks.models import TaskCompletion
    from django.db.models import Exists, OuterRef, Q
    
    # Obtener preferencias del usuario
    today = timezone.now().date()
    
    # Calcular rangos de fechas según preferencias
    def get_date_range(range_type):
        if range_type == 'today':
            return today, today
        elif range_type == 'week':
            week_start = today - timedelta(days=today.weekday())
            week_end = week_start + timedelta(days=6)
            return week_start, week_end
        elif range_type == 'month':
            month_start = today.replace(day=1)
            if today.month == 12:
                month_end = today.replace(year=today.year + 1, month=1, day=1) - timedelta(days=1)
            else:
                month_end = today.replace(month=today.month + 1, day=1) - timedelta(days=1)
            return month_start, month_end
        return None, None  # 'all'
    
    # Estadísticas de tareas pendientes (basadas en preferencias)
    pending_query = Task.objects.filter(
        group_id__in=user_group_ids
    ).exclude(
        Exists(TaskCompletion.objects.filter(task=OuterRef('pk'), user=request.user, completed=True))
    )
    
    if request.user.pending_range != 'all':
        start_date, end_date = get_date_range(request.user.pending_range)
        if start_date and end_date:
            pending_query = pending_query.filter(due_date__gte=start_date, due_date__lte=end_date)
    
    pending_tasks_count = pending_query.count()
    
    # Estadísticas de tareas completadas (basadas en preferencias)
    completed_query = TaskCompletion.objects.filter(
        task__group_id__in=user_group_ids,
        user=request.user,
        completed=True
    )
    
    if request.user.completed_range != 'all':
        start_date, end_date = get_date_range(request.user.completed_range)
        if start_date and end_date:
            completed_query = completed_query.filter(completed_at__date__gte=start_date, completed_at__date__lte=end_date)
    
    completed_tasks_count = completed_query.count()
    
    # Tareas vencidas (basadas en preferencias)
    overdue_query = Task.objects.filter(
        group_id__in=user_group_ids,
        due_date__lt=today
    ).exclude(
        Exists(TaskCompletion.objects.filter(task=OuterRef('pk'), user=request.user, completed=True))
    )
    
    if request.user.overdue_range == 'today':
        overdue_query = overdue_query.filter(due_date=today - timedelta(days=1))
    elif request.user.overdue_range == '7days':
        overdue_query = overdue_query.filter(due_date__gte=today - timedelta(days=7))
    elif request.user.overdue_range == '30days':
        overdue_query = overdue_query.filter(due_date__gte=today - timedelta(days=30))
    # 'all' no aplica filtro adicional
    
    overdue_tasks_count = overdue_query.count()
    
    # Próximas tareas (próximos 7 días, pendientes para el usuario)
    upcoming_tasks = Task.objects.filter(
        group_id__in=user_group_ids,
        due_date__gte=timezone.now().date(),
        due_date__lte=timezone.now().date() + timedelta(days=7)
    ).exclude(
        Exists(TaskCompletion.objects.filter(task=OuterRef('pk'), user=request.user, completed=True))
    ).select_related('subject', 'group', 'created_by').annotate(
        user_completed=Exists(TaskCompletion.objects.filter(task=OuterRef('pk'), user=request.user, completed=True))
    ).order_by('due_date')[:5]
    
    # Tareas recientes (últimas 5 creadas)
    recent_tasks = Task.objects.filter(
        group_id__in=user_group_ids
    ).select_related('subject', 'group', 'created_by').annotate(
        user_completed=Exists(TaskCompletion.objects.filter(task=OuterRef('pk'), user=request.user, completed=True))
    ).order_by('-created_at')[:5]
    
    # Actividad reciente (tareas que el usuario completó recientemente)
    recent_activity = TaskCompletion.objects.filter(
        task__group_id__in=user_group_ids,
        user=request.user,
        completed=True
    ).select_related('task', 'task__subject', 'task__group', 'task__created_by').order_by('-completed_at')[:5]
    
    # Estadísticas por grupo (basadas en el estado personal del usuario)
    group_stats = []
    if multigroup_mode == 'unified':
        # En modo unificado, mostrar estadísticas de todos los grupos
        for membership in user_groups:
            group = membership.group
            group_pending = Task.objects.filter(group=group).exclude(
                Exists(TaskCompletion.objects.filter(task=OuterRef('pk'), user=request.user, completed=True))
            ).count()
            group_completed = Task.objects.filter(group=group).filter(
                Exists(TaskCompletion.objects.filter(task=OuterRef('pk'), user=request.user, completed=True))
            ).count()
            group_stats.append({
                'group': group,
                'pending': group_pending,
                'completed': group_completed,
                'total': group_pending + group_completed
            })
    else:
        # En modo separado, mostrar solo el grupo activo
        if request.user.last_active_group_id:
            active_membership = user_groups.filter(group_id=request.user.last_active_group_id).first()
            if active_membership:
                group = active_membership.group
                group_pending = Task.objects.filter(group=group).exclude(
                    Exists(TaskCompletion.objects.filter(task=OuterRef('pk'), user=request.user, completed=True))
                ).count()
                group_completed = Task.objects.filter(group=group).filter(
                    Exists(TaskCompletion.objects.filter(task=OuterRef('pk'), user=request.user, completed=True))
                ).count()
                group_stats.append({
                    'group': group,
                    'pending': group_pending,
                    'completed': group_completed,
                    'total': group_pending + group_completed
                })
    
    # Generar URLs con filtros según configuración del usuario
    from urllib.parse import urlencode
    
    # Mapeo de rangos a etiquetas legibles
    range_labels = {
        'today': 'Hoy',
        'week': 'Esta semana',
        'month': 'Este mes',
        'all': 'Todas'
    }
    
    overdue_labels = {
        'today': 'Hoy',
        '7days': 'Últimos 7 días',
        '30days': 'Últimos 30 días',
        'all': 'Todas'
    }
    
    # Obtener etiquetas según configuración del usuario
    pending_range_label = range_labels.get(request.user.pending_range, 'Todas')
    completed_range_label = range_labels.get(request.user.completed_range, 'Todas')
    overdue_range_label = overdue_labels.get(request.user.overdue_range, 'Todas')
    
    # URL para tareas pendientes
    pending_params = {'status': 'pending'}
    if request.user.pending_range == 'today':
        pending_params['time'] = 'today'
    elif request.user.pending_range == 'week':
        pending_params['time'] = 'this_week'
    # 'month' y 'all' no tienen filtro de tiempo específico en la vista de tareas
    
    # URL para tareas completadas
    completed_params = {'status': 'completed'}
    if request.user.completed_range == 'today':
        completed_params['time'] = 'today'
    elif request.user.completed_range == 'week':
        completed_params['time'] = 'this_week'
    
    # URL para tareas vencidas
    overdue_params = {'time': 'overdue'}
    
    # Determinar a dónde redirigir según configuración
    dashboard_groups_count = dashboard_groups.count() if dashboard_groups.exists() else 0
    
    # Lógica de redirección mejorada
    if multigroup_mode == 'separated' and dashboard_groups_count == 1:
        # Modo separado con 1 grupo configurado: ir directo a group_tasks de ese grupo
        group_id = user_group_ids[0]
        pending_tasks_url = f"{reverse('group_tasks', kwargs={'group_id': group_id})}?{urlencode(pending_params)}"
        completed_tasks_url = f"{reverse('group_tasks', kwargs={'group_id': group_id})}?{urlencode(completed_params)}"
        overdue_tasks_url = f"{reverse('group_tasks', kwargs={'group_id': group_id})}?{urlencode(overdue_params)}"
    
    elif multigroup_mode == 'separated' and dashboard_groups_count > 1:
        # Modo separado con 2+ grupos configurados: ir a unified_tasks con filtro
        group_ids = ','.join(str(g_id) for g_id in user_group_ids)
        pending_params['groups'] = group_ids
        completed_params['groups'] = group_ids
        overdue_params['groups'] = group_ids
        pending_tasks_url = f"{reverse('task_list')}?{urlencode(pending_params)}"
        completed_tasks_url = f"{reverse('task_list')}?{urlencode(completed_params)}"
        overdue_tasks_url = f"{reverse('task_list')}?{urlencode(overdue_params)}"
    
    elif multigroup_mode == 'unified' and dashboard_groups_count >= 1:
        # Modo unificado con grupos configurados: ir a unified_tasks con filtro
        group_ids = ','.join(str(g_id) for g_id in user_group_ids)
        pending_params['groups'] = group_ids
        completed_params['groups'] = group_ids
        overdue_params['groups'] = group_ids
        pending_tasks_url = f"{reverse('task_list')}?{urlencode(pending_params)}"
        completed_tasks_url = f"{reverse('task_list')}?{urlencode(completed_params)}"
        overdue_tasks_url = f"{reverse('task_list')}?{urlencode(overdue_params)}"
    
    elif multigroup_mode == 'unified':
        # Modo unificado sin grupos configurados: mostrar todos
        pending_tasks_url = f"{reverse('task_list')}?{urlencode(pending_params)}"
        completed_tasks_url = f"{reverse('task_list')}?{urlencode(completed_params)}"
        overdue_tasks_url = f"{reverse('task_list')}?{urlencode(overdue_params)}"
    
    else:
        # Modo separado sin grupos configurados: usar grupo activo o seleccionar
        if request.user.last_active_group_id:
            group_id = request.user.last_active_group_id
            pending_tasks_url = f"{reverse('group_tasks', kwargs={'group_id': group_id})}?{urlencode(pending_params)}"
            completed_tasks_url = f"{reverse('group_tasks', kwargs={'group_id': group_id})}?{urlencode(completed_params)}"
            overdue_tasks_url = f"{reverse('group_tasks', kwargs={'group_id': group_id})}?{urlencode(overdue_params)}"
        elif user_groups_count == 1:
            group_id = user_groups.first().group.id
            pending_tasks_url = f"{reverse('group_tasks', kwargs={'group_id': group_id})}?{urlencode(pending_params)}"
            completed_tasks_url = f"{reverse('group_tasks', kwargs={'group_id': group_id})}?{urlencode(completed_params)}"
            overdue_tasks_url = f"{reverse('group_tasks', kwargs={'group_id': group_id})}?{urlencode(overdue_params)}"
        else:
            # Sin grupo activo, ir a la lista de tareas (selección)
            pending_tasks_url = f"{reverse('task_list')}?{urlencode(pending_params)}"
            completed_tasks_url = f"{reverse('task_list')}?{urlencode(completed_params)}"
            overdue_tasks_url = f"{reverse('task_list')}?{urlencode(overdue_params)}"
    
    context = {
        'has_groups': has_groups,
        'user_groups_count': user_groups_count,
        'user_groups': user_groups,
        'pending_requests': pending_requests,
        'pending_tasks_count': pending_tasks_count,
        'completed_tasks_count': completed_tasks_count,
        'overdue_tasks_count': overdue_tasks_count,
        'upcoming_tasks': upcoming_tasks,
        'recent_tasks': recent_tasks,
        'recent_activity': recent_activity,
        'group_stats': group_stats,
        'pending_tasks_url': pending_tasks_url,
        'completed_tasks_url': completed_tasks_url,
        'overdue_tasks_url': overdue_tasks_url,
        'pending_range_label': pending_range_label,
        'completed_range_label': completed_range_label,
        'overdue_range_label': overdue_range_label,
        'multigroup_mode': multigroup_mode,
    }
    return render(request, 'Dashboard/dashboard.html', context)


@login_required
def delete_account(request):
    """Vista para eliminar la cuenta del usuario"""
    from django.http import JsonResponse
    from django.contrib.auth import logout
    
    if request.method == 'POST':
        try:
            user = request.user
            
            # Eliminar el usuario (esto eliminará en cascada sus datos relacionados)
            user.delete()
            
            # Cerrar sesión
            logout(request)
            
            return JsonResponse({
                'success': True,
                'message': 'Cuenta eliminada exitosamente'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
    
    return JsonResponse({
        'success': False,
        'error': 'Método no permitido'
    }, status=405)
