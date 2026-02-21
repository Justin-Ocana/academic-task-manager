from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from datetime import datetime, timedelta
from calendar import monthrange
from apps.tasks.models import Task, TaskCompletion
from apps.groups.models import GroupMember
from apps.subjects.models import Subject


@login_required
def calendar_view(request):
    """Vista principal del calendario"""
    # Obtener grupos del usuario
    user_groups = GroupMember.objects.filter(user=request.user).select_related('group')
    
    # Obtener modo multigrupo
    multigroup_mode = request.user.multigroup_mode
    
    # Siempre mostrar calendario con todos los grupos
    # El filtrado se hace en el frontend
    group_ids = user_groups.values_list('group_id', flat=True)
    subjects = Subject.objects.filter(group_id__in=group_ids).select_related('group')
    
    context = {
        'user_groups': user_groups,
        'subjects': subjects,
        'multigroup_mode': multigroup_mode,
    }
    return render(request, 'calendar_app/calendar.html', context)


@login_required
def calendar_data(request):
    """API para obtener datos del calendario"""
    # Obtener parámetros
    year = int(request.GET.get('year', timezone.now().year))
    month = int(request.GET.get('month', timezone.now().month))
    view_type = request.GET.get('view', 'month')  # month o week
    
    # Filtros
    group_id = request.GET.get('group')
    subject_id = request.GET.get('subject')
    status_filter = request.GET.get('status')  # pending, completed, overdue
    creator_id = request.GET.get('creator')
    
    # Obtener grupos del usuario
    user_group_ids = GroupMember.objects.filter(user=request.user).values_list('group_id', flat=True)
    
    # Determinar qué grupos mostrar según el modo multigrupo
    multigroup_mode = request.user.multigroup_mode
    
    # Siempre permitir ver todos los grupos, pero en modo separado preseleccionar el activo
    if group_id:
        # Si se especifica un grupo en el filtro, usarlo
        filtered_group_ids = [int(group_id)]
    elif multigroup_mode == 'separated' and request.user.last_active_group_id:
        # En modo separado, usar el grupo activo por defecto
        filtered_group_ids = [request.user.last_active_group_id]
    else:
        # Mostrar todos los grupos
        filtered_group_ids = list(user_group_ids)
    
    # Construir query de tareas
    tasks_query = Task.objects.filter(group_id__in=filtered_group_ids).select_related(
        'subject', 'group', 'created_by'
    )
    
    # Aplicar filtros adicionales
    if subject_id:
        tasks_query = tasks_query.filter(subject_id=subject_id)
    if creator_id:
        tasks_query = tasks_query.filter(created_by_id=creator_id)
    
    # Obtener fecha actual
    today = timezone.now().date()
    
    # Filtrar por rango de fechas según vista
    if view_type == 'month':
        start_date = datetime(year, month, 1).date()
        _, last_day = monthrange(year, month)
        end_date = datetime(year, month, last_day).date()
    else:  # week
        # Obtener día específico del parámetro o usar hoy
        day = int(request.GET.get('day', timezone.now().day))
        week_date = datetime(year, month, day).date()
        # Calcular inicio de semana (domingo = 0)
        start_date = week_date - timedelta(days=week_date.weekday() + 1)
        if week_date.weekday() == 6:  # Si es domingo
            start_date = week_date
        end_date = start_date + timedelta(days=6)
    
    # Aplicar filtro de fechas
    # Si no hay filtro de estado, mostrar tareas del mes Y vencidas anteriores
    if not status_filter:
        # Mostrar tareas del mes actual + tareas vencidas de meses anteriores
        tasks_query = tasks_query.filter(due_date__lte=end_date)
    else:
        # Con filtro, solo mostrar tareas del rango
        tasks_query = tasks_query.filter(due_date__gte=start_date, due_date__lte=end_date)
    
    # Obtener tareas
    tasks = []
    
    for task in tasks_query:
        # Actualizar estado de la tarea
        task.update_status()
        
        # Obtener estado del usuario actual
        completion = TaskCompletion.objects.filter(task=task, user=request.user).first()
        user_completed = completion.completed if completion else False
        
        # Determinar si está vencida
        is_overdue = task.due_date < today
        is_archived = task.status == 'archived'
        
        # LÓGICA DE FILTRADO
        if status_filter == 'overdue':
            # Filtro VENCIDAS: Mostrar TODAS las vencidas (completadas o no)
            if not is_overdue:
                continue
            # Mostrar si está completada o no
            if user_completed:
                task_status = 'overdue_completed'
                color_class = 'success'
            else:
                task_status = 'overdue'
                color_class = 'danger'
            
        elif status_filter == 'completed':
            # Filtro COMPLETADAS: Solo completadas que NO estén vencidas
            if not user_completed or is_overdue:
                continue
            task_status = 'completed'
            color_class = 'success'
            
        elif status_filter == 'pending':
            # Filtro PENDIENTES: Solo pendientes que NO estén vencidas ni completadas
            if user_completed or is_overdue:
                continue
            task_status = 'pending'
            color_class = 'warning'
            
        elif status_filter == 'archived':
            # Filtro ARCHIVADAS: Solo tareas archivadas
            if not is_archived:
                continue
            task_status = 'archived'
            color_class = 'secondary'
            
        else:
            # SIN FILTRO: Mostrar TODAS (pendientes, completadas Y vencidas)
            if is_archived:
                task_status = 'archived'
                color_class = 'secondary'
            elif is_overdue:
                if user_completed:
                    task_status = 'overdue_completed'
                    color_class = 'success'
                else:
                    task_status = 'overdue'
                    color_class = 'danger'
            elif user_completed:
                task_status = 'completed'
                color_class = 'success'
            else:
                task_status = 'pending'
                color_class = 'warning'
        
        tasks.append({
            'id': task.id,
            'title': task.title,
            'subject': task.subject.name,
            'subject_color': task.subject.color,
            'group': task.group.name,
            'due_date': task.due_date.isoformat(),
            'assigned_date': task.assigned_date.isoformat(),
            'status': task_status,
            'color_class': color_class,
            'priority': task.priority,
            'created_by': f"{task.created_by.nombre} {task.created_by.apellido}" if task.created_by else "Desconocido",
            'description': task.description[:100] if task.description else "",
            'is_archived': is_archived,
        })
    
    # Calcular carga de trabajo por semana (solo con las tareas filtradas)
    workload = calculate_weekly_workload(tasks, start_date, end_date)
    
    return JsonResponse({
        'tasks': tasks,
        'workload': workload,
        'start_date': start_date.isoformat(),
        'end_date': end_date.isoformat(),
    })


def calculate_weekly_workload(tasks_list, start_date, end_date):
    """Calcula la carga de trabajo para la semana actual o la semana visible en vista semanal"""
    from datetime import datetime as dt
    
    # Obtener la fecha actual
    today = timezone.now().date()
    
    # Determinar si estamos en vista semanal o mensual
    # Si el rango es de 7 días o menos, es vista semanal
    days_diff = (end_date - start_date).days
    
    if days_diff <= 7:
        # Vista semanal: usar el rango que se pasa (la semana visible)
        week_start = start_date
        week_end = end_date
    else:
        # Vista mensual: calcular la semana actual (donde está hoy)
        week_start = today - timedelta(days=today.weekday() + 1)
        if today.weekday() == 6:  # Si es domingo
            week_start = today
        week_end = week_start + timedelta(days=6)
    
    # Contar tareas de la semana
    week_tasks = set()
    
    for task in tasks_list:
        task_date = dt.fromisoformat(task['due_date']).date()
        
        # Contar tareas dentro de la semana
        if week_start <= task_date <= week_end:
            week_tasks.add(task['id'])
    
    # Si no hay tareas en la semana, retornar lista vacía
    if not week_tasks:
        return []
    
    task_count = len(week_tasks)
    
    # Determinar nivel de carga
    if task_count <= 3:
        level = 'light'
        label = 'Semana liviana'
    elif task_count <= 6:
        level = 'medium'
        label = 'Semana media'
    elif task_count <= 10:
        level = 'heavy'
        label = 'Semana llena'
    else:
        level = 'extreme'
        label = 'Semana pesada 🔥'
    
    # Retornar la semana
    return [{
        'start': week_start.isoformat(),
        'end': week_end.isoformat(),
        'task_count': task_count,
        'level': level,
        'label': label,
    }]


@login_required
def day_details(request, year, month, day):
    """Obtener detalles de un día específico"""
    date = datetime(year, month, day).date()
    today = timezone.now().date()
    
    # Obtener grupos del usuario
    user_group_ids = GroupMember.objects.filter(user=request.user).values_list('group_id', flat=True)
    
    # Obtener tareas del día (incluyendo vencidas)
    tasks = Task.objects.filter(
        group_id__in=user_group_ids,
        due_date=date
    ).select_related('subject', 'group', 'created_by')
    
    tasks_data = []
    for task in tasks:
        completion = TaskCompletion.objects.filter(task=task, user=request.user).first()
        user_completed = completion.completed if completion else False
        is_overdue = task.due_date < today
        
        # Determinar estado
        if is_overdue:
            if user_completed:
                status = 'overdue_completed'
            else:
                status = 'overdue'
        elif user_completed:
            status = 'completed'
        else:
            status = 'pending'
        
        tasks_data.append({
            'id': task.id,
            'title': task.title,
            'subject': task.subject.name,
            'subject_color': task.subject.color,
            'group': task.group.name,
            'description': task.description,
            'priority': task.priority,
            'completed': user_completed,
            'is_overdue': is_overdue,
            'status': status,
            'created_by': f"{task.created_by.nombre} {task.created_by.apellido}" if task.created_by else "Desconocido",
        })
    
    return JsonResponse({
        'date': date.isoformat(),
        'tasks': tasks_data,
        'task_count': len(tasks_data),
    })


@login_required
def set_active_group(request):
    """Establecer el grupo activo para el modo separado"""
    if request.method == 'POST':
        group_id = request.POST.get('group_id')
        
        if not group_id:
            return JsonResponse({'success': False, 'error': 'No se especificó grupo'}, status=400)
        
        try:
            group_id = int(group_id)
            # Verificar que el usuario pertenece al grupo
            membership = GroupMember.objects.filter(user=request.user, group_id=group_id).first()
            
            if not membership:
                return JsonResponse({'success': False, 'error': 'No perteneces a este grupo'}, status=403)
            
            # Guardar el grupo activo
            request.user.last_active_group_id = group_id
            request.user.save(update_fields=['last_active_group_id'])
            
            return JsonResponse({
                'success': True,
                'group_id': group_id,
                'group_name': membership.group.name
            })
            
        except (ValueError, TypeError):
            return JsonResponse({'success': False, 'error': 'ID de grupo inválido'}, status=400)
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)
