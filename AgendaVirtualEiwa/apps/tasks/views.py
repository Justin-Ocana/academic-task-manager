from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.urls import reverse
from django.db.models import Q
from apps.groups.models import Group, GroupMember
from apps.subjects.models import Subject
from apps.notifications.utils import create_notification
from apps.tracking.utils import log_task_action, create_revertible_action
from .models import Task
from .forms import TaskForm


@login_required
def task_list(request):
    """Lista unificada de tareas con filtros o selección de grupo"""
    user_groups = GroupMember.objects.filter(user=request.user).select_related('group')
    user_groups_count = user_groups.count()
    
    # Verificar modo multigrupo del usuario
    multigroup_mode = request.user.multigroup_mode
    
    # Si hay parámetro 'groups', siempre mostrar vista unificada (incluso en modo separado)
    groups_filter = request.GET.get('groups', '')
    
    if groups_filter:
        # Hay filtro de grupos específicos, mostrar vista unificada
        return unified_tasks_view(request, user_groups, preselect_active_group=False)
    
    # Si solo tiene 1 grupo, ir directo a ese grupo (independiente del modo)
    if user_groups_count == 1:
        single_group = user_groups.first().group
        return redirect('group_tasks', group_id=single_group.id)
    
    # Si el modo es separado y tiene más de 1 grupo
    if multigroup_mode == 'separated':
        # Mostrar página de selección
        context = {
            'user_groups': user_groups,
            'multigroup_mode': 'separated',
        }
        return render(request, 'tasks/select_group.html', context)
    
    # Modo unificado con 2+ grupos: mostrar vista unificada
    return unified_tasks_view(request, user_groups, preselect_active_group=False)


def unified_tasks_view(request, user_groups, preselect_active_group=False):
    """Vista unificada de tareas de todos los grupos"""
    from datetime import timedelta
    from .models import TaskCompletion
    from django.db.models import Exists, OuterRef, Q
    
    today = timezone.now().date()
    
    # Obtener IDs de todos los grupos del usuario
    user_group_ids = list(user_groups.values_list('group_id', flat=True))
    
    # Filtros
    status_filter = request.GET.get('status', '')
    group_filter = request.GET.get('group', '')
    groups_filter = request.GET.get('groups', '')  # Nuevo: filtro de múltiples grupos
    subject_filter = request.GET.get('subject', '')
    time_filter = request.GET.get('time', '')
    sort_by = request.GET.get('sort', 'due_date')
    
    # En modo separado, preseleccionar el grupo activo si no hay filtro
    if preselect_active_group and not group_filter and not groups_filter and request.user.last_active_group_id:
        group_filter = str(request.user.last_active_group_id)
    
    # Query base: todas las tareas de todos los grupos
    tasks = Task.objects.filter(group_id__in=user_group_ids).select_related(
        'subject', 'group', 'created_by'
    ).annotate(
        user_completed=Exists(
            TaskCompletion.objects.filter(
                task=OuterRef('pk'),
                user=request.user,
                completed=True
            )
        )
    )
    
    # Filtro por múltiples grupos (prioritario sobre filtro de grupo único)
    filtered_groups = []
    if groups_filter:
        try:
            # Parsear IDs de grupos separados por coma
            selected_group_ids = [int(gid.strip()) for gid in groups_filter.split(',') if gid.strip().isdigit()]
            # Filtrar solo grupos a los que el usuario pertenece
            selected_group_ids = [gid for gid in selected_group_ids if gid in user_group_ids]
            if selected_group_ids:
                tasks = tasks.filter(group_id__in=selected_group_ids)
                group_filter = 'multiple'  # Marcar que hay filtro de múltiples grupos
                # Obtener los objetos de grupo para mostrar sus nombres
                from apps.groups.models import Group
                filtered_groups = list(Group.objects.filter(id__in=selected_group_ids).values_list('name', flat=True))
        except (ValueError, AttributeError):
            pass
    # Filtro por grupo específico (solo si no hay filtro de múltiples grupos)
    elif group_filter and group_filter != 'all':
        tasks = tasks.filter(group_id=group_filter)
    
    # Filtro por estado
    if status_filter == 'completed':
        tasks = tasks.filter(user_completed=True).exclude(status='archived')
    elif status_filter == 'pending':
        tasks = tasks.filter(Q(user_completed=False) | Q(user_completed__isnull=True), status='pending')
    elif status_filter == 'archived':
        tasks = tasks.filter(status='archived')
    else:
        # Por defecto: mostrar solo activas
        tasks = tasks.exclude(status='archived')
    
    # Filtro por materia
    if subject_filter and subject_filter != 'all':
        tasks = tasks.filter(subject_id=subject_filter)
    
    # Filtro por tiempo
    if status_filter != 'archived':
        if not time_filter:
            tasks = tasks.filter(due_date__gte=today)
        elif time_filter == 'today':
            tasks = tasks.filter(due_date=today)
        elif time_filter == 'tomorrow':
            tasks = tasks.filter(due_date=today + timedelta(days=1))
        elif time_filter == 'this_week':
            week_end = today + timedelta(days=(6 - today.weekday()))
            tasks = tasks.filter(due_date__gte=today, due_date__lte=week_end)
        elif time_filter == 'next_week':
            next_week_start = today + timedelta(days=(7 - today.weekday()))
            next_week_end = next_week_start + timedelta(days=6)
            tasks = tasks.filter(due_date__gte=next_week_start, due_date__lte=next_week_end)
        elif time_filter == 'overdue':
            tasks = tasks.filter(due_date__lt=today)
    
    # Ordenamiento
    if sort_by == 'due_date':
        tasks = tasks.order_by('due_date', '-created_at')
    elif sort_by == 'due_date_desc':
        tasks = tasks.order_by('-due_date', '-created_at')
    elif sort_by == 'created':
        tasks = tasks.order_by('-created_at')
    elif sort_by == 'subject':
        tasks = tasks.order_by('subject__name', 'due_date')
    elif sort_by == 'group':
        tasks = tasks.order_by('group__name', 'due_date')
    
    # Obtener todas las materias de todos los grupos
    subjects = Subject.objects.filter(group_id__in=user_group_ids).select_related('group')
    
    # Crear diccionario con roles del usuario en cada grupo
    user_roles = {}
    for membership in user_groups:
        user_roles[membership.group_id] = {
            'is_leader': membership.role == 'leader',
            'role': membership.role
        }
    
    # Verificar si el usuario puede crear tareas (al menos en un grupo)
    can_create_in_any_group = False
    for membership in user_groups:
        group = membership.group
        is_leader = membership.role == 'leader'
        if (group.task_create_permission == 'all' or 
            group.task_create_permission == 'approval' or 
            (group.task_create_permission == 'leader' and is_leader)):
            can_create_in_any_group = True
            break
    
    context = {
        'tasks': tasks,
        'user_groups': user_groups,
        'subjects': subjects,
        'can_create': can_create_in_any_group,
        'status_filter': status_filter,
        'group_filter': group_filter,
        'filtered_groups': filtered_groups,
        'subject_filter': subject_filter,
        'time_filter': time_filter,
        'sort_by': sort_by,
        'is_unified_view': True,
        'multigroup_mode': 'unified',
        'user_roles': user_roles,
    }
    
    return render(request, 'tasks/unified_tasks.html', context)


@login_required
def group_tasks(request, group_id):
    """Ver tareas de un grupo específico"""
    group = get_object_or_404(Group, id=group_id)
    
    try:
        membership = GroupMember.objects.get(group=group, user=request.user)
        is_leader = membership.role == 'leader'
    except GroupMember.DoesNotExist:
        return redirect('task_list')
    
    # Guardar el último grupo activo si está en modo separado
    if request.user.multigroup_mode == 'separated':
        if request.user.last_active_group_id != group_id:
            request.user.last_active_group_id = group_id
            request.user.save(update_fields=['last_active_group_id'])
    
    # Filtros
    from datetime import timedelta
    today = timezone.now().date()
    
    status_filter = request.GET.get('status', '')
    subject_filter = request.GET.get('subject', '')
    time_filter = request.GET.get('time', '')
    sort_by = request.GET.get('sort', 'due_date')
    
    from .models import TaskCompletion
    from django.db.models import Exists, OuterRef, Q
    
    # Obtener tareas y anotar con el estado personal del usuario
    tasks = Task.objects.filter(group=group).select_related('subject', 'created_by').annotate(
        user_completed=Exists(
            TaskCompletion.objects.filter(
                task=OuterRef('pk'),
                user=request.user,
                completed=True
            )
        )
    )
    
    # Filtro por estado
    if status_filter == 'completed':
        # Solo completadas
        tasks = tasks.filter(user_completed=True).exclude(status='archived')
    elif status_filter == 'pending':
        # Solo pendientes (no completadas, no archivadas)
        tasks = tasks.filter(Q(user_completed=False) | Q(user_completed__isnull=True), status='pending')
    elif status_filter == 'archived':
        # Solo archivadas
        tasks = tasks.filter(status='archived')
    else:
        # Por defecto: mostrar solo activas (pendientes y vencidas recientes, NO archivadas)
        tasks = tasks.exclude(status='archived')
    
    # Filtro por materia
    if subject_filter and subject_filter != 'all':
        tasks = tasks.filter(subject_id=subject_filter)
    
    # Filtro por tiempo (solo si NO estamos viendo archivadas)
    if status_filter != 'archived':
        if not time_filter:
            # Sin filtro de tiempo: mostrar SOLO pendientes (NO vencidas, NO archivadas)
            tasks = tasks.filter(due_date__gte=today)
        elif time_filter == 'today':
            tasks = tasks.filter(due_date=today)
        elif time_filter == 'tomorrow':
            tasks = tasks.filter(due_date=today + timedelta(days=1))
        elif time_filter == 'this_week':
            week_end = today + timedelta(days=(6 - today.weekday()))
            tasks = tasks.filter(due_date__gte=today, due_date__lte=week_end)
        elif time_filter == 'next_week':
            next_week_start = today + timedelta(days=(7 - today.weekday()))
            next_week_end = next_week_start + timedelta(days=6)
            tasks = tasks.filter(due_date__gte=next_week_start, due_date__lte=next_week_end)
        elif time_filter == 'overdue':
            # Mostrar TODAS las vencidas (completadas o no)
            tasks = tasks.filter(due_date__lt=today)
    
    # Ordenamiento
    if sort_by == 'due_date':
        tasks = tasks.order_by('due_date', '-created_at')
    elif sort_by == 'due_date_desc':
        tasks = tasks.order_by('-due_date', '-created_at')
    elif sort_by == 'created':
        tasks = tasks.order_by('-created_at')
    elif sort_by == 'subject':
        tasks = tasks.order_by('subject__name', 'due_date')
    
    subjects = Subject.objects.filter(group=group)
    
    # Verificar permisos
    can_create = (group.task_create_permission == 'all' or 
                  group.task_create_permission == 'approval' or 
                  (group.task_create_permission == 'leader' and is_leader))
    
    # Solicitudes pendientes (para líderes y creadores según configuración)
    pending_task_requests = []
    pending_edit_requests = []
    
    from .models import TaskRequest, TaskEditRequest
    
    if is_leader:
        # Líder ve todas las solicitudes
        pending_task_requests = TaskRequest.objects.filter(
            group=group,
            status='pending'
        ).select_related('subject', 'requested_by').order_by('-created_at')
        
        pending_edit_requests = TaskEditRequest.objects.filter(
            task__group=group,
            status='pending'
        ).select_related('task', 'task__subject', 'requested_by').order_by('-created_at')
    elif group.task_edit_permission == 'approval_leader_creator':
        # Creador solo ve solicitudes de edición de sus propias tareas
        pending_edit_requests = TaskEditRequest.objects.filter(
            task__group=group,
            task__created_by=request.user,
            status='pending'
        ).select_related('task', 'task__subject', 'requested_by').order_by('-created_at')
    
    context = {
        'group': group,
        'tasks': tasks,
        'subjects': subjects,
        'is_leader': is_leader,
        'can_create': can_create,
        'status_filter': status_filter,
        'subject_filter': subject_filter,
        'time_filter': time_filter,
        'sort_by': sort_by,
        'pending_task_requests': pending_task_requests,
        'pending_edit_requests': pending_edit_requests,
    }
    
    return render(request, 'tasks/group_tasks.html', context)


@login_required
def create_task(request, group_id):
    """Crear tarea"""
    group = get_object_or_404(Group, id=group_id)
    
    try:
        membership = GroupMember.objects.get(group=group, user=request.user)
        is_leader = membership.role == 'leader'
    except GroupMember.DoesNotExist:
        return redirect('task_list')
    
    # Verificar permisos
    if group.task_create_permission == 'leader' and not is_leader:
        return redirect('group_tasks', group_id=group_id)
    
    # Verificar si requiere aprobación
    needs_approval = group.task_create_permission == 'approval' and not is_leader
    
    # Verificar si puede subir documentos
    can_upload_documents = False
    documents_need_approval = False
    if group.documents_enabled:
        if group.document_upload_permission == 'all':
            can_upload_documents = True
        elif group.document_upload_permission == 'leader':
            can_upload_documents = is_leader
        elif group.document_upload_permission == 'approval':
            can_upload_documents = True
            documents_need_approval = True
    
    if request.method == 'POST':
        form = TaskForm(request.POST, group=group)
        if form.is_valid():
            # Moderación de contenido
            from apps.core.moderation import ContentModerator
            
            title = f"{form.cleaned_data['subject'].name}"
            description = form.cleaned_data.get('description', '')
            
            # Obtener modo de moderación del grupo
            moderation_mode = group.content_moderation
            
            is_valid, error_message, censored_title, censored_description = ContentModerator.moderate_task(
                title, description, mode=moderation_mode
            )
            
            if not is_valid:
                form.add_error(None, error_message)
                context = {
                    'form': form,
                    'group': group,
                    'is_leader': is_leader,
                    'needs_approval': needs_approval,
                    'can_upload_documents': can_upload_documents,
                    'documents_need_approval': documents_need_approval,
                }
                return render(request, 'tasks/task_form.html', context)
            
            # REGLA CLAVE: Si hay documentos Y el permiso es "con aprobación" → SIEMPRE es solicitud
            has_attachments = can_upload_documents and 'attachments' in request.FILES and len(request.FILES.getlist('attachments')) > 0
            force_approval_by_documents = has_attachments and documents_need_approval
            
            # Determinar si va a solicitud
            requires_task_approval = needs_approval or force_approval_by_documents
            
            # Si requiere aprobación (por texto O por documentos), crear solicitud en vez de tarea
            if requires_task_approval:
                from .models import TaskRequest, TaskRequestAttachment
                from apps.notifications.utils import notify_group_leaders
                
                # Usar descripción censurada si aplica
                final_description = censored_description if moderation_mode == 'censor' else form.cleaned_data['description']
                
                # Crear solicitud de tarea
                task_request = TaskRequest.objects.create(
                    group=group,
                    subject=form.cleaned_data['subject'],
                    title=f"{form.cleaned_data['subject'].name}",
                    description=final_description,
                    assigned_date=form.cleaned_data['assigned_date'],
                    due_date=form.cleaned_data['due_date'],
                    priority=form.cleaned_data.get('priority', 'medium'),
                    requested_by=request.user,
                    message=request.POST.get('request_message', '')
                )
                
                # Guardar archivos físicamente si los hay
                if has_attachments:
                    files = request.FILES.getlist('attachments')
                    for file in files:
                        TaskRequestAttachment.objects.create(
                            task_request=task_request,
                            file=file,
                            original_filename=file.name,
                            file_size=file.size,
                            file_type=file.content_type
                        )
                
                # Notificar a los líderes
                reason = 'con documentos adjuntos' if force_approval_by_documents else ''
                notify_group_leaders(
                    group=group,
                    notification_type='general',
                    title='Nueva solicitud de tarea',
                    message=f'{request.user.nombre} solicita crear tarea de {task_request.subject.name} {reason}',
                    sender=request.user,
                    action_url=reverse('group_requests', kwargs={'group_id': group.id})
                )
                
                # Redirigir según modo multigrupo
                if request.user.multigroup_mode == 'unified':
                    return redirect('task_list')
                else:
                    return redirect('group_tasks', group_id=group_id)
            
            # Crear tarea directamente (sin aprobación)
            task = form.save(commit=False)
            task.group = group
            task.created_by = request.user
            # Generar título automático basado en la materia
            if task.subject:
                task.title = f"{task.subject.name}"
            else:
                task.title = "Tarea"
            
            # Aplicar censura si está activada
            if moderation_mode == 'censor':
                task.description = censored_description
            
            task.save()
            
            # Procesar archivos adjuntos si hay
            if can_upload_documents and 'attachments' in request.FILES:
                from .models import TaskAttachment
                files = request.FILES.getlist('attachments')
                
                for file in files:
                    attachment = TaskAttachment(
                        task=task,
                        uploaded_by=request.user,
                        original_filename=file.name,
                        file_size=file.size,
                        file_type=file.content_type,
                        file=file
                    )
                    
                    # Establecer estado según permisos
                    if documents_need_approval:
                        attachment.status = 'pending'
                    else:
                        attachment.status = 'approved'
                    
                    attachment.save()
            
            # Registrar en tracking
            log_task_action(
                task=task,
                action='created',
                user=request.user,
                details={
                    'subject': task.subject.name if task.subject else None,
                    'due_date': str(task.due_date),
                    'description': task.description[:100] if task.description else None
                }
            )
            
            # Notificar a todos los miembros
            members = GroupMember.objects.filter(group=group).exclude(user=request.user)
            for member in members:
                create_notification(
                    recipient=member.user,
                    notification_type='general',
                    title='Nueva tarea',
                    message=f'{request.user.nombre} agregó tarea de {task.subject.name if task.subject else "sin materia"}',
                    sender=request.user,
                    action_url=reverse('group_tasks', kwargs={'group_id': group.id})
                )
            
            # Redirigir según modo multigrupo
            if request.user.multigroup_mode == 'unified':
                return redirect('task_list')
            else:
                return redirect('group_tasks', group_id=group_id)
    else:
        form = TaskForm(group=group)
    
    subjects = Subject.objects.filter(group=group)
    today = timezone.now().date()
    context = {
        'group': group,
        'form': form,
        'subjects': subjects,
        'today': today,
        'needs_approval': needs_approval,
        'can_upload_documents': can_upload_documents,
        'documents_need_approval': documents_need_approval,
    }
    return render(request, 'tasks/task_form.html', context)


@login_required
def task_detail(request, task_id):
    """Ver detalles de una tarea"""
    task = get_object_or_404(Task, id=task_id)
    
    # Actualizar estado de la tarea
    task.update_status()
    
    try:
        membership = GroupMember.objects.get(group=task.group, user=request.user)
        is_leader = membership.role == 'leader'
    except GroupMember.DoesNotExist:
        return redirect('task_list')
    
    # Verificar permisos de edición y eliminación
    edit_perm = task.group.task_edit_permission
    
    if edit_perm == 'all':
        can_edit = True
    elif edit_perm == 'approval':
        can_edit = True  # Todos pueden editar pero requiere aprobación
    elif edit_perm == 'approval_leader_creator':
        can_edit = True  # Todos pueden editar pero requiere aprobación del líder o creador
    elif edit_perm == 'leader':
        can_edit = is_leader
    else:
        can_edit = False
    
    can_delete = (is_leader or 
                  task.group.task_delete_permission == 'all' or 
                  (task.group.task_delete_permission == 'leader_creator' and task.created_by == request.user))
    
    # Obtener el estado personal del usuario para esta tarea
    from .models import TaskCompletion, TaskAttachment
    try:
        completion = TaskCompletion.objects.get(task=task, user=request.user)
        user_completed = completion.completed
    except TaskCompletion.DoesNotExist:
        user_completed = False
    
    # Obtener documentos adjuntos
    if task.group.documents_enabled:
        # Filtrar documentos según permisos
        if is_leader:
            # El líder ve todos los documentos
            attachments = TaskAttachment.objects.filter(task=task).order_by('-uploaded_at')
        else:
            # Los miembros solo ven documentos aprobados y los suyos propios
            attachments = TaskAttachment.objects.filter(
                task=task
            ).filter(
                Q(status='approved') | Q(uploaded_by=request.user)
            ).order_by('-uploaded_at')
        
        attachments_count = attachments.filter(status='approved').count()
        
        # Verificar permisos de subida
        can_upload = False
        if task.group.document_upload_permission == 'all':
            can_upload = True
        elif task.group.document_upload_permission == 'leader':
            can_upload = is_leader
        elif task.group.document_upload_permission == 'approval':
            can_upload = True
    else:
        attachments = []
        attachments_count = 0
        can_upload = False
    
    # Obtener modo multigrupo para el botón de volver
    multigroup_mode = request.user.multigroup_mode
    
    context = {
        'task': task,
        'group': task.group,
        'is_leader': is_leader,
        'can_edit': can_edit,
        'can_delete': can_delete,
        'user_completed': user_completed,
        'multigroup_mode': multigroup_mode,
        'attachments': attachments,
        'attachments_count': attachments_count,
        'can_upload_documents': can_upload,
    }
    
    return render(request, 'tasks/task_detail.html', context)


@login_required
def edit_task(request, task_id):
    """Editar tarea"""
    task = get_object_or_404(Task, id=task_id)
    
    # Actualizar estado y bloquear edición de archivadas
    task.update_status()
    if task.status == 'archived':
        return redirect('task_detail', task_id=task.id)
    
    try:
        membership = GroupMember.objects.get(group=task.group, user=request.user)
        is_leader = membership.role == 'leader'
    except GroupMember.DoesNotExist:
        return redirect('task_list')
    
    # Verificar permisos
    edit_permission = task.group.task_edit_permission
    is_creator = task.created_by == request.user
    
    # Si es líder, siempre puede editar
    if is_leader:
        can_edit_directly = True
        needs_approval = False
    # Si el permiso es 'all', puede editar directamente
    elif edit_permission == 'all':
        can_edit_directly = True
        needs_approval = False
    # Si el permiso es 'approval', puede editar pero requiere aprobación del líder
    elif edit_permission == 'approval':
        can_edit_directly = False
        needs_approval = True
    # Si el permiso es 'approval_leader_creator', puede editar pero requiere aprobación del líder o creador
    elif edit_permission == 'approval_leader_creator':
        can_edit_directly = False
        needs_approval = True
    # Si el permiso es 'leader', solo el líder puede editar
    elif edit_permission == 'leader':
        return redirect('group_tasks', group_id=task.group.id)
    else:
        return redirect('group_tasks', group_id=task.group.id)
    
    # Verificar permisos de documentos
    can_upload_documents = False
    documents_need_approval = False
    if task.group.documents_enabled:
        if task.group.document_upload_permission == 'all':
            can_upload_documents = True
        elif task.group.document_upload_permission == 'leader':
            can_upload_documents = is_leader
        elif task.group.document_upload_permission == 'approval':
            can_upload_documents = True
            documents_need_approval = True
    
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task, group=task.group)
        if form.is_valid():
            # Moderación de contenido
            from apps.core.moderation import ContentModerator
            
            subject = form.cleaned_data.get('subject')
            title = f"{subject.name}" if subject else "Tarea"
            description = form.cleaned_data.get('description', '')
            
            # Obtener modo de moderación del grupo
            moderation_mode = task.group.content_moderation
            
            is_valid, error_message, censored_title, censored_description = ContentModerator.moderate_task(
                title, description, mode=moderation_mode
            )
            
            if not is_valid:
                form.add_error(None, error_message)
                context = {
                    'form': form,
                    'task': task,
                    'group': task.group,
                    'is_leader': is_leader,
                    'needs_approval': needs_approval,
                }
                return render(request, 'tasks/task_form.html', context)
            
            # Usar el contenido censurado si aplica
            if moderation_mode == 'censor':
                form.cleaned_data['description'] = censored_description
            
            # Verificar si hay archivos nuevos adjuntos
            has_new_attachments = can_upload_documents and 'attachments' in request.FILES and len(request.FILES.getlist('attachments')) > 0
            
            # REGLA: Si hay archivos nuevos Y el permiso es "con aprobación" → SIEMPRE va a solicitud
            force_approval_by_documents = has_new_attachments and documents_need_approval
            
            # Determinar si va a solicitud (por texto O por documentos)
            requires_edit_approval = needs_approval or force_approval_by_documents
            
            # Si requiere aprobación (por texto O por documentos), crear solicitud
            if requires_edit_approval:
                from .models import TaskEditRequest
                from apps.notifications.utils import notify_group_leaders
                
                # RECARGAR la tarea desde la base de datos
                task.refresh_from_db()
                
                # Guardar SOLO los campos que cambiaron
                proposed_changes = {}
                
                # Descripción (usar versión censurada si aplica)
                new_desc = (censored_description if moderation_mode == 'censor' else form.cleaned_data.get('description', '')).strip()
                old_desc = (task.description or '').strip()
                print(f"DEBUG Desc - Old: '{old_desc}' | New: '{new_desc}' | Changed: {new_desc != old_desc}")
                if new_desc != old_desc:
                    proposed_changes['description'] = new_desc
                
                # Materia
                new_subject = form.cleaned_data.get('subject')
                print(f"DEBUG Subject - Old ID: {task.subject_id} | New ID: {new_subject.id if new_subject else None} | Changed: {new_subject and new_subject.id != task.subject_id}")
                if new_subject and new_subject.id != task.subject_id:
                    proposed_changes['subject_id'] = new_subject.id
                    proposed_changes['subject_name'] = new_subject.name
                
                # Fecha de entrega
                new_due = form.cleaned_data.get('due_date')
                print(f"DEBUG Due - Old: {task.due_date} | New: {new_due} | Changed: {new_due and str(new_due) != str(task.due_date)}")
                if new_due and str(new_due) != str(task.due_date):
                    proposed_changes['due_date'] = str(new_due)
                
                # Fecha mandada
                new_assigned = form.cleaned_data.get('assigned_date')
                print(f"DEBUG Assigned - Old: {task.assigned_date} | New: {new_assigned} | Changed: {new_assigned and str(new_assigned) != str(task.assigned_date)}")
                if new_assigned and str(new_assigned) != str(task.assigned_date):
                    proposed_changes['assigned_date'] = str(new_assigned)
                
                print(f"DEBUG FINAL - proposed_changes: {proposed_changes}")
                
                # Obtener documentos a eliminar
                documents_to_delete = []
                if 'delete_attachments' in request.POST:
                    documents_to_delete = [int(id) for id in request.POST.getlist('delete_attachments')]
                
                # Crear solicitud de edición
                edit_request = TaskEditRequest.objects.create(
                    task=task,
                    requested_by=request.user,
                    proposed_changes=proposed_changes,
                    message=request.POST.get('edit_message', ''),
                    documents_to_delete=documents_to_delete if documents_to_delete else None
                )
                
                # Guardar nuevos documentos adjuntos si los hay
                if can_upload_documents and 'attachments' in request.FILES:
                    from .models import TaskEditAttachment
                    files = request.FILES.getlist('attachments')
                    
                    for file in files:
                        TaskEditAttachment.objects.create(
                            edit_request=edit_request,
                            file=file,
                            original_filename=file.name,
                            file_size=file.size,
                            file_type=file.content_type
                        )
                
                # Notificar a los líderes
                notify_group_leaders(
                    group=task.group,
                    notification_type='general',
                    title='Solicitud de edición de tarea',
                    message=f'{request.user.nombre} quiere editar la tarea de {task.subject.name}',
                    sender=request.user,
                    action_url=reverse('group_requests', kwargs={'group_id': task.group.id})
                )
                
                # Si el permiso es approval_leader_creator, también notificar al creador
                if task.group.task_edit_permission == 'approval_leader_creator' and task.created_by != request.user:
                    create_notification(
                        recipient=task.created_by,
                        notification_type='general',
                        title='Solicitud de edición de tu tarea',
                        message=f'{request.user.nombre} quiere editar tu tarea de {task.subject.name}',
                        sender=request.user,
                        action_url=reverse('group_requests', kwargs={'group_id': task.group.id})
                    )
                
                # Redirigir según modo multigrupo
                if request.user.multigroup_mode == 'unified':
                    return redirect('task_list')
                else:
                    return redirect('group_tasks', group_id=task.group.id)
            
            # Si puede editar directamente
            else:
                # Guardar valores originales para tracking
                old_values = {
                    'description': task.description,
                    'subject_id': task.subject_id,
                    'due_date': task.due_date,
                    'assigned_date': task.assigned_date,
                    'priority': task.priority,
                }
                
                updated_task = form.save(commit=False)
                # Actualizar título basado en la materia
                if updated_task.subject:
                    updated_task.title = f"{updated_task.subject.name}"
                else:
                    updated_task.title = "Tarea"
                
                # Aplicar censura si está activada
                if moderation_mode == 'censor':
                    updated_task.description = censored_description
                
                updated_task.save()
                
                # Registrar cambios en tracking
                changes = []
                if old_values['description'] != updated_task.description:
                    log_task_action(task, 'edited', request.user, 'description', old_values['description'], updated_task.description)
                    changes.append('description')
                if old_values['subject_id'] != updated_task.subject_id:
                    old_subject = Subject.objects.get(id=old_values['subject_id']).name if old_values['subject_id'] else 'Sin materia'
                    new_subject = updated_task.subject.name if updated_task.subject else 'Sin materia'
                    log_task_action(task, 'edited', request.user, 'subject', old_subject, new_subject)
                    changes.append('subject')
                if old_values['due_date'] != updated_task.due_date:
                    log_task_action(task, 'edited', request.user, 'due_date', str(old_values['due_date']), str(updated_task.due_date))
                    changes.append('due_date')
                if old_values['assigned_date'] != updated_task.assigned_date:
                    log_task_action(task, 'edited', request.user, 'assigned_date', str(old_values['assigned_date']), str(updated_task.assigned_date))
                    changes.append('assigned_date')
                if old_values['priority'] != updated_task.priority:
                    log_task_action(task, 'edited', request.user, 'priority', old_values['priority'], updated_task.priority)
                    changes.append('priority')
                
                # Procesar documentos eliminados - ELIMINAR INMEDIATAMENTE
                deleted_attachments = []
                if 'delete_attachments' in request.POST:
                    from .models import TaskAttachment
                    delete_ids = request.POST.getlist('delete_attachments')
                    for att_id in delete_ids:
                        try:
                            attachment = TaskAttachment.objects.get(id=att_id, task=task)
                            deleted_attachments.append(int(att_id))
                            # Eliminar archivo físicamente de inmediato
                            if attachment.file:
                                try:
                                    attachment.file.delete()
                                except:
                                    pass
                            attachment.delete()
                            log_task_action(task, 'document_deleted', request.user, 'attachment', attachment.original_filename, '')
                        except:
                            pass
                
                # Crear acción revertible con documentos eliminados (pero ya borrados físicamente)
                if changes or deleted_attachments:
                    snapshot_data = old_values.copy()
                    if deleted_attachments:
                        snapshot_data['deleted_attachments'] = deleted_attachments
                        snapshot_data['deleted_permanently'] = True  # Marcar que ya se eliminaron
                    
                    create_revertible_action(
                        action_type='task_edit',
                        group=task.group,
                        performed_by=request.user,
                        snapshot_data=snapshot_data,
                        task=task
                    )
                
                # Procesar nuevos documentos
                if can_upload_documents and 'attachments' in request.FILES:
                    from .models import TaskAttachment
                    from django.conf import settings
                    import os
                    
                    files = request.FILES.getlist('attachments')
                    
                    for file in files:
                        # Validar tamaño
                        if file.size > settings.MAX_UPLOAD_SIZE:
                            max_size_mb = settings.MAX_UPLOAD_SIZE / (1024 * 1024)
                            form.add_error(None, f'El archivo "{file.name}" es demasiado grande. Máximo: {max_size_mb} MB')
                            continue
                        
                        # Validar tipo
                        if file.content_type not in settings.ALLOWED_DOCUMENT_TYPES:
                            form.add_error(None, f'El archivo "{file.name}" no es un tipo permitido')
                            continue
                        
                        # Validar extensión
                        ext = os.path.splitext(file.name)[1].lower()
                        allowed_extensions = ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.txt']
                        if ext not in allowed_extensions:
                            form.add_error(None, f'La extensión de "{file.name}" no está permitida')
                            continue
                        
                        # Bloquear extensiones peligrosas
                        dangerous_extensions = ['.exe', '.bat', '.cmd', '.sh', '.js', '.jar', '.zip', '.rar']
                        if ext in dangerous_extensions:
                            form.add_error(None, f'El archivo "{file.name}" está bloqueado por seguridad')
                            continue
                        
                        attachment = TaskAttachment(
                            task=task,
                            uploaded_by=request.user,
                            original_filename=file.name,
                            file_size=file.size,
                            file_type=file.content_type,
                            file=file
                        )
                        
                        if documents_need_approval:
                            attachment.status = 'pending'
                        else:
                            attachment.status = 'approved'
                        
                        attachment.save()
                        log_task_action(task, 'document_added', request.user, 'attachment', '', file.name)
                
                # Solo redirigir si no hay errores
                if not form.errors:
                    # Redirigir según modo multigrupo
                    if request.user.multigroup_mode == 'unified':
                        return redirect('task_list')
                    else:
                        return redirect('group_tasks', group_id=task.group.id)
    else:
        form = TaskForm(instance=task, group=task.group)
    
    # Obtener documentos existentes
    from .models import TaskAttachment
    existing_attachments = TaskAttachment.objects.filter(task=task).order_by('-uploaded_at')
    
    subjects = Subject.objects.filter(group=task.group)
    today = task.assigned_date
    context = {
        'group': task.group,
        'form': form,
        'task': task,
        'subjects': subjects,
        'today': today,
        'needs_approval': needs_approval,
        'existing_attachments': existing_attachments,
        'can_upload_documents': can_upload_documents,
        'documents_need_approval': documents_need_approval,
    }
    return render(request, 'tasks/task_form.html', context)


@login_required
def delete_task(request, task_id):
    """Eliminar tarea"""
    task = get_object_or_404(Task, id=task_id)
    
    # Actualizar estado
    task.update_status()
    
    try:
        membership = GroupMember.objects.get(group=task.group, user=request.user)
        is_leader = membership.role == 'leader'
    except GroupMember.DoesNotExist:
        return redirect('task_list')
    
    # Si la tarea está archivada, solo el líder puede eliminarla
    if task.status == 'archived' and not is_leader:
        return redirect('task_detail', task_id=task.id)
    
    # Verificar permisos
    can_delete = (task.group.task_delete_permission == 'leader' and is_leader) or \
                 (task.group.task_delete_permission == 'leader_creator' and (is_leader or task.created_by == request.user)) or \
                 (task.group.task_delete_permission == 'all')
    
    if not can_delete:
        return redirect('group_tasks', group_id=task.group.id)
    
    group_id = task.group.id
    group = task.group
    task_title = task.title
    subject_name = task.subject.name if task.subject else None
    
    # Guardar snapshot antes de eliminar
    snapshot = {
        'title': task.title,
        'description': task.description,
        'subject_id': task.subject_id,
        'due_date': str(task.due_date),
        'assigned_date': str(task.assigned_date),
        'priority': task.priority,
        'group_id': task.group_id,
        'created_by_id': task.created_by_id,
    }
    
    # Crear acción revertible ANTES de eliminar
    create_revertible_action(
        action_type='task_delete',
        group=group,
        performed_by=request.user,
        snapshot_data=snapshot,
        task=task
    )
    
    # Eliminar tarea
    task.delete()
    
    # Registrar eliminación en tracking DESPUÉS de eliminar
    from apps.tracking.models import TaskHistory
    TaskHistory.objects.create(
        task=None,
        task_title=task_title,
        group=group,
        action='deleted',
        user=request.user,
        details={'task_title': task_title, 'subject': subject_name}
    )
    
    # Redirigir según modo multigrupo
    if request.user.multigroup_mode == 'unified':
        return redirect('task_list')
    else:
        return redirect('group_tasks', group_id=group_id)


@login_required
def toggle_task_status(request, task_id):
    """Marcar tarea como completada/pendiente (estado personal por usuario)"""
    from .models import TaskCompletion
    from django.http import JsonResponse
    
    task = get_object_or_404(Task, id=task_id)
    
    try:
        GroupMember.objects.get(group=task.group, user=request.user)
    except GroupMember.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'No tienes acceso a esta tarea'}, status=403)
    
    # Actualizar estado de la tarea antes de verificar
    task.update_status()
    
    # Verificar si la tarea puede ser completada
    if not task.can_be_completed:
        return JsonResponse({
            'success': False, 
            'error': 'Esta tarea fue archivada por antigüedad y ya no puede completarse.',
            'archived': True
        }, status=400)
    
    # Obtener o crear el estado personal del usuario para esta tarea
    completion, created = TaskCompletion.objects.get_or_create(
        task=task,
        user=request.user,
        defaults={'completed': False}
    )
    
    # Alternar el estado
    if completion.completed:
        completion.completed = False
        completion.completed_at = None
        action = 'reopened'
    else:
        completion.completed = True
        completion.completed_at = timezone.now()
        action = 'completed'
    
    completion.save()
    
    # Registrar cambio de estado personal
    log_task_action(
        task=task,
        action=action,
        user=request.user,
        details={'personal_status': 'completed' if completion.completed else 'pending'}
    )
    
    # Si es petición AJAX explícita, devolver JSON
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'completed': completion.completed,
            'action': action
        })
    
    # Para formularios POST normales, redirigir
    return redirect('group_tasks', group_id=task.group.id)



@login_required
def approve_task_request(request, request_id):
    """Aprobar solicitud de creación de tarea"""
    from .models import TaskRequest
    
    task_request = get_object_or_404(TaskRequest, id=request_id)
    
    # Verificar que es líder del grupo
    try:
        GroupMember.objects.get(group=task_request.group, user=request.user, role='leader')
    except GroupMember.DoesNotExist:
        return redirect('group_tasks', group_id=task_request.group.id)
    
    # Aprobar y crear la tarea
    task_request.status = 'approved'
    task_request.reviewed_by = request.user
    task_request.reviewed_at = timezone.now()
    task_request.save()
    
    # Crear la tarea
    task = Task.objects.create(
        group=task_request.group,
        subject=task_request.subject,
        title=task_request.title,
        description=task_request.description,
        assigned_date=task_request.assigned_date,
        due_date=task_request.due_date,
        priority=task_request.priority,
        created_by=task_request.requested_by,
        status='pending'
    )
    
    # Registrar en tracking
    log_task_action(
        task=task,
        action='created',
        user=task_request.requested_by,
        details={
            'subject': task.subject.name,
            'due_date': str(task.due_date),
            'approved_by': request.user.id,
            'was_request': True
        }
    )
    
    # Notificar al solicitante
    create_notification(
        recipient=task_request.requested_by,
        notification_type='general',
        title='Tarea aprobada',
        message=f'Tu solicitud de tarea de {task.subject.name} ha sido aprobada',
        sender=request.user,
        action_url=reverse('task_detail', kwargs={'task_id': task.id})
    )
    
    # Notificar a todos los miembros
    members = GroupMember.objects.filter(group=task_request.group).exclude(user__in=[request.user, task_request.requested_by])
    for member in members:
        create_notification(
            recipient=member.user,
            notification_type='general',
            title='Nueva tarea',
            message=f'{task_request.requested_by.nombre} agregó tarea de {task.subject.name}',
            sender=task_request.requested_by,
            action_url=reverse('task_detail', kwargs={'task_id': task.id})
        )
    
    return redirect('group_requests', group_id=task_request.group.id)


@login_required
def reject_task_request(request, request_id):
    """Rechazar solicitud de creación de tarea"""
    from .models import TaskRequest
    
    task_request = get_object_or_404(TaskRequest, id=request_id)
    
    # Verificar que es líder del grupo
    try:
        GroupMember.objects.get(group=task_request.group, user=request.user, role='leader')
    except GroupMember.DoesNotExist:
        return redirect('group_requests', group_id=task_request.group.id)
    
    # Rechazar
    task_request.status = 'rejected'
    task_request.reviewed_by = request.user
    task_request.reviewed_at = timezone.now()
    task_request.save()
    
    # Notificar al solicitante
    create_notification(
        recipient=task_request.requested_by,
        notification_type='general',
        title='Tarea rechazada',
        message=f'Tu solicitud de tarea de {task_request.subject.name} ha sido rechazada',
        sender=request.user
    )
    
    return redirect('group_requests', group_id=task_request.group.id)


@login_required
def approve_edit_request(request, request_id):
    """Aprobar solicitud de edición de tarea"""
    from .models import TaskEditRequest
    
    edit_request = get_object_or_404(TaskEditRequest, id=request_id)
    task = edit_request.task
    
    # Verificar permisos: líder o creador (si el permiso lo permite)
    try:
        membership = GroupMember.objects.get(group=task.group, user=request.user)
        is_leader = membership.role == 'leader'
    except GroupMember.DoesNotExist:
        return redirect('group_tasks', group_id=task.group.id)
    
    is_creator = task.created_by == request.user
    can_approve = is_leader or (is_creator and task.group.task_edit_permission == 'approval_leader_creator')
    
    if not can_approve:
        return redirect('group_tasks', group_id=task.group.id)
    
    # Aprobar y aplicar cambios
    edit_request.status = 'approved'
    edit_request.reviewed_by = request.user
    edit_request.reviewed_at = timezone.now()
    edit_request.save()
    
    task = edit_request.task
    old_values = {}
    
    # Aplicar cambios propuestos
    for field, value in edit_request.proposed_changes.items():
        # Ignorar campos que no son del modelo (como subject_name que es solo para mostrar)
        if field == 'subject_name':
            continue
            
        old_value = getattr(task, field)
        # Convertir objetos date a string para serialización JSON
        if hasattr(old_value, 'isoformat'):
            old_values[field] = old_value.isoformat()
        else:
            old_values[field] = old_value
        
        if field == 'subject_id':
            task.subject_id = value
            task.title = Subject.objects.get(id=value).name
        elif field in ['due_date', 'assigned_date']:
            from datetime import datetime
            setattr(task, field, datetime.strptime(value, '%Y-%m-%d').date())
        else:
            setattr(task, field, value)
    
    task.save()
    
    # Crear acción revertible
    if old_values:
        create_revertible_action(
            action_type='task_edit',
            group=task.group,
            performed_by=edit_request.requested_by,
            snapshot_data=old_values,
            task=task
        )
    
    # Registrar en tracking
    for field, old_value in old_values.items():
        new_value = getattr(task, field)
        if old_value != new_value:
            # Para subject_id, mostrar el nombre de la materia en lugar del ID
            if field == 'subject_id':
                old_subject_name = Subject.objects.get(id=old_value).name if old_value else 'Sin materia'
                new_subject_name = task.subject.name if task.subject else 'Sin materia'
                log_task_action(
                    task=task,
                    action='edited',
                    user=edit_request.requested_by,
                    field_changed='subject',
                    old_value=old_subject_name,
                    new_value=new_subject_name,
                    details={'approved_by': request.user.id}
                )
            else:
                log_task_action(
                    task=task,
                    action='edited',
                    user=edit_request.requested_by,
                    field_changed=field,
                    old_value=str(old_value),
                    new_value=str(new_value),
                    details={'approved_by': request.user.id}
                )
    
    # Notificar al solicitante
    create_notification(
        recipient=edit_request.requested_by,
        notification_type='general',
        title='Edición aprobada',
        message=f'Tus cambios en la tarea de {task.subject.name} han sido aprobados',
        sender=request.user,
        action_url=reverse('task_detail', kwargs={'task_id': task.id})
    )
    
    return redirect('group_requests', group_id=task.group.id)


@login_required
def reject_edit_request(request, request_id):
    """Rechazar solicitud de edición de tarea"""
    from .models import TaskEditRequest
    
    edit_request = get_object_or_404(TaskEditRequest, id=request_id)
    task = edit_request.task
    
    # Verificar permisos: líder o creador (si el permiso lo permite)
    try:
        membership = GroupMember.objects.get(group=task.group, user=request.user)
        is_leader = membership.role == 'leader'
    except GroupMember.DoesNotExist:
        return redirect('group_tasks', group_id=task.group.id)
    
    is_creator = task.created_by == request.user
    can_reject = is_leader or (is_creator and task.group.task_edit_permission == 'approval_leader_creator')
    
    if not can_reject:
        return redirect('group_tasks', group_id=task.group.id)
    
    # Rechazar
    edit_request.status = 'rejected'
    edit_request.reviewed_by = request.user
    edit_request.reviewed_at = timezone.now()
    edit_request.save()
    
    # Notificar al solicitante
    create_notification(
        recipient=edit_request.requested_by,
        notification_type='general',
        title='Edición rechazada',
        message=f'Tus cambios propuestos en la tarea de {edit_request.task.subject.name} han sido rechazados',
        sender=request.user,
        action_url=reverse('task_detail', kwargs={'task_id': edit_request.task.id})
    )
    
    return redirect('group_requests', group_id=edit_request.task.group.id)



@login_required
def approve_task_request(request, request_id):
    """Aprobar solicitud de creación de tarea"""
    from .models import TaskRequest, TaskAttachment, TaskRequestAttachment
    from django.core.files import File
    import shutil
    import os
    
    task_request = get_object_or_404(TaskRequest, id=request_id)
    
    # Verificar que es líder
    try:
        membership = GroupMember.objects.get(group=task_request.group, user=request.user)
        if membership.role != 'leader':
            return redirect('group_requests', group_id=task_request.group.id)
    except GroupMember.DoesNotExist:
        return redirect('requests_list')
    
    if task_request.status != 'pending':
        return redirect('group_requests', group_id=task_request.group.id)
    
    # Crear la tarea
    task = Task.objects.create(
        group=task_request.group,
        subject=task_request.subject,
        title=task_request.title,
        description=task_request.description,
        assigned_date=task_request.assigned_date,
        due_date=task_request.due_date,
        priority=task_request.priority,
        created_by=task_request.requested_by,
        status='pending'
    )
    
    # Copiar archivos adjuntos de la solicitud a la tarea
    temp_attachments = TaskRequestAttachment.objects.filter(task_request=task_request)
    for temp_att in temp_attachments:
        if temp_att.file:
            # Crear nuevo attachment para la tarea
            task_attachment = TaskAttachment(
                task=task,
                uploaded_by=task_request.requested_by,
                original_filename=temp_att.original_filename,
                file_size=temp_att.file_size,
                file_type=temp_att.file_type,
                status='approved'
            )
            
            # Copiar el archivo
            with temp_att.file.open('rb') as f:
                task_attachment.file.save(temp_att.original_filename, File(f), save=True)
    
    # Marcar solicitud como aprobada
    task_request.status = 'approved'
    task_request.reviewed_by = request.user
    task_request.reviewed_at = timezone.now()
    task_request.save()
    
    # Eliminar archivos temporales
    for temp_att in temp_attachments:
        if temp_att.file:
            temp_att.file.delete()
        temp_att.delete()
    
    # Registrar en tracking
    log_task_action(
        task=task,
        action='created',
        user=request.user,
        details={'approved_from_request': True, 'requested_by': task_request.requested_by.id}
    )
    
    # Notificar al solicitante
    create_notification(
        recipient=task_request.requested_by,
        notification_type='general',
        title='Solicitud aprobada',
        message=f'Tu solicitud de tarea de {task.subject.name} ha sido aprobada',
        sender=request.user,
        action_url=reverse('task_detail', kwargs={'task_id': task.id})
    )
    
    # Notificar a todos los miembros del grupo
    members = GroupMember.objects.filter(group=task_request.group).exclude(user__in=[request.user, task_request.requested_by])
    for member in members:
        create_notification(
            recipient=member.user,
            notification_type='general',
            title='Nueva tarea',
            message=f'Nueva tarea de {task.subject.name}',
            sender=request.user,
            action_url=reverse('task_detail', kwargs={'task_id': task.id})
        )
    
    return redirect('group_requests', group_id=task_request.group.id)


@login_required
def reject_task_request(request, request_id):
    """Rechazar solicitud de creación de tarea"""
    from .models import TaskRequest, TaskRequestAttachment
    
    task_request = get_object_or_404(TaskRequest, id=request_id)
    
    # Verificar que es líder
    try:
        membership = GroupMember.objects.get(group=task_request.group, user=request.user)
        if membership.role != 'leader':
            return redirect('group_requests', group_id=task_request.group.id)
    except GroupMember.DoesNotExist:
        return redirect('requests_list')
    
    if task_request.status != 'pending':
        return redirect('group_requests', group_id=task_request.group.id)
    
    # Eliminar archivos temporales físicamente
    temp_attachments = TaskRequestAttachment.objects.filter(task_request=task_request)
    for temp_att in temp_attachments:
        if temp_att.file:
            try:
                temp_att.file.delete()  # Elimina el archivo físico
            except:
                pass
        temp_att.delete()  # Elimina el registro de BD
    
    # Marcar como rechazada
    task_request.status = 'rejected'
    task_request.reviewed_by = request.user
    task_request.reviewed_at = timezone.now()
    task_request.save()
    
    # Notificar al solicitante
    create_notification(
        recipient=task_request.requested_by,
        notification_type='general',
        title='Solicitud rechazada',
        message=f'Tu solicitud de tarea de {task_request.subject.name} ha sido rechazada',
        sender=request.user
    )
    
    return redirect('group_requests', group_id=task_request.group.id)


@login_required
def approve_edit_request(request, request_id):
    """Aprobar solicitud de edición de tarea"""
    from .models import TaskEditRequest, TaskAttachment, TaskEditAttachment
    from django.core.files import File
    
    edit_request = get_object_or_404(TaskEditRequest, id=request_id)
    task = edit_request.task
    
    # Verificar permisos
    try:
        membership = GroupMember.objects.get(group=task.group, user=request.user)
        is_leader = membership.role == 'leader'
        is_creator = task.created_by == request.user
    except GroupMember.DoesNotExist:
        return redirect('requests_list')
    
    # Verificar si puede aprobar
    can_approve = is_leader or (is_creator and task.group.task_edit_permission == 'approval_leader_creator')
    
    if not can_approve or edit_request.status != 'pending':
        return redirect('group_requests', group_id=task.group.id)
    
    # Aplicar cambios en campos
    proposed_changes = edit_request.proposed_changes
    
    for field, new_value in proposed_changes.items():
        if field == 'subject_id':
            task.subject_id = int(new_value)
            task.title = f"{Subject.objects.get(id=new_value).name}"
        elif field != 'subject_name':  # Ignorar campo auxiliar
            setattr(task, field, new_value)
    
    task.save()
    
    # Eliminar documentos marcados
    if edit_request.documents_to_delete:
        for att_id in edit_request.documents_to_delete:
            try:
                attachment = TaskAttachment.objects.get(id=att_id, task=task)
                if attachment.file:
                    attachment.file.delete()
                attachment.delete()
                log_task_action(task, 'document_deleted', request.user, 'attachment', attachment.original_filename, '')
            except TaskAttachment.DoesNotExist:
                pass
    
    # Agregar nuevos documentos
    new_attachments = TaskEditAttachment.objects.filter(edit_request=edit_request)
    for temp_att in new_attachments:
        if temp_att.file:
            # Crear nuevo attachment para la tarea
            task_attachment = TaskAttachment(
                task=task,
                uploaded_by=edit_request.requested_by,
                original_filename=temp_att.original_filename,
                file_size=temp_att.file_size,
                file_type=temp_att.file_type,
                status='approved'
            )
            
            # Copiar el archivo
            with temp_att.file.open('rb') as f:
                task_attachment.file.save(temp_att.original_filename, File(f), save=True)
            
            log_task_action(task, 'document_added', request.user, 'attachment', '', temp_att.original_filename)
    
    # Marcar como aprobada
    edit_request.status = 'approved'
    edit_request.reviewed_by = request.user
    edit_request.reviewed_at = timezone.now()
    edit_request.save()
    
    # Eliminar archivos temporales
    for temp_att in new_attachments:
        if temp_att.file:
            temp_att.file.delete()
        temp_att.delete()
    
    # Registrar en tracking
    log_task_action(
        task=task,
        action='edited',
        user=request.user,
        details={'approved_edit_request': True, 'requested_by': edit_request.requested_by.id}
    )
    
    # Notificar al solicitante
    create_notification(
        recipient=edit_request.requested_by,
        notification_type='general',
        title='Edición aprobada',
        message=f'Tu solicitud de edición para {task.subject.name} ha sido aprobada',
        sender=request.user,
        action_url=reverse('task_detail', kwargs={'task_id': task.id})
    )
    
    return redirect('group_requests', group_id=task.group.id)


@login_required
def reject_edit_request(request, request_id):
    """Rechazar solicitud de edición de tarea"""
    from .models import TaskEditRequest, TaskEditAttachment
    
    edit_request = get_object_or_404(TaskEditRequest, id=request_id)
    task = edit_request.task
    
    # Verificar permisos
    try:
        membership = GroupMember.objects.get(group=task.group, user=request.user)
        is_leader = membership.role == 'leader'
        is_creator = task.created_by == request.user
    except GroupMember.DoesNotExist:
        return redirect('requests_list')
    
    # Verificar si puede rechazar
    can_reject = is_leader or (is_creator and task.group.task_edit_permission == 'approval_leader_creator')
    
    if not can_reject or edit_request.status != 'pending':
        return redirect('group_requests', group_id=task.group.id)
    
    # Eliminar archivos temporales físicamente
    new_attachments = TaskEditAttachment.objects.filter(edit_request=edit_request)
    for temp_att in new_attachments:
        if temp_att.file:
            try:
                temp_att.file.delete()  # Elimina el archivo físico
            except:
                pass
        temp_att.delete()  # Elimina el registro de BD
    
    # Marcar como rechazada
    edit_request.status = 'rejected'
    edit_request.reviewed_by = request.user
    edit_request.reviewed_at = timezone.now()
    edit_request.save()
    
    # Notificar al solicitante
    create_notification(
        recipient=edit_request.requested_by,
        notification_type='general',
        title='Edición rechazada',
        message=f'Tu solicitud de edición para {task.subject.name} ha sido rechazada',
        sender=request.user
    )
    
    return redirect('group_requests', group_id=task.group.id)
