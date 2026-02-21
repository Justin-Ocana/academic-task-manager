from django.db import models
from django.conf import settings


class Task(models.Model):
    """Modelo de Tarea"""
    
    STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('overdue_recent', 'Vencida reciente'),
        ('completed', 'Completada'),
        ('archived', 'Archivada'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Baja'),
        ('medium', 'Media'),
        ('high', 'Alta'),
    ]
    
    group = models.ForeignKey('groups.Group', on_delete=models.CASCADE, related_name='tasks')
    subject = models.ForeignKey('subjects.Subject', on_delete=models.CASCADE, related_name='tasks')
    title = models.CharField(max_length=200, verbose_name="Título")
    description = models.TextField(blank=True, verbose_name="Descripción")
    pages = models.CharField(max_length=100, blank=True, verbose_name="Páginas")
    
    # Fechas
    assigned_date = models.DateField(verbose_name="Fecha mandada")
    due_date = models.DateField(verbose_name="Fecha de entrega")
    
    # Estado y prioridad
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    
    # Metadata
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='created_tasks')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    archived_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.title} - {self.subject.name}"
    
    def get_computed_status(self):
        """Calcula el estado actual basado en fechas y completado"""
        from django.utils import timezone
        from datetime import timedelta
        
        today = timezone.now().date()
        
        # Si está completada, siempre es completada
        if self.status == 'completed':
            return 'completed'
        
        # Si está archivada, siempre es archivada
        if self.status == 'archived':
            return 'archived'
        
        # Si la fecha de entrega es hoy o futura
        if self.due_date >= today:
            return 'pending'
        
        # Si está vencida
        days_overdue = (today - self.due_date).days
        
        # Vencida reciente (hasta 30 días)
        if days_overdue <= 30:
            return 'overdue_recent'
        
        # Debe archivarse (más de 30 días)
        return 'archived'
    
    def update_status(self):
        """Actualiza el estado de la tarea según las reglas del sistema"""
        from django.utils import timezone
        
        new_status = self.get_computed_status()
        
        if new_status != self.status:
            old_status = self.status
            self.status = new_status
            
            if new_status == 'archived' and not self.archived_at:
                self.archived_at = timezone.now()
            
            self.save()
            
            # Registrar cambio en historial
            from apps.tracking.utils import log_task_action
            log_task_action(
                task=self,
                action='status_changed',
                user=None,
                field_changed='status',
                old_value=old_status,
                new_value=new_status,
                details={'automatic': True, 'reason': 'Sistema de archivado automático'}
            )
    
    @property
    def is_overdue(self):
        """Verifica si la tarea está vencida"""
        from django.utils import timezone
        if self.status in ['pending', 'overdue_recent']:
            return timezone.now().date() > self.due_date
        return False
    
    @property
    def can_be_completed(self):
        """Verifica si la tarea puede ser completada"""
        return self.status in ['pending', 'overdue_recent']
    
    @property
    def days_overdue(self):
        """Calcula cuántos días lleva vencida la tarea"""
        from django.utils import timezone
        if self.is_overdue:
            return (timezone.now().date() - self.due_date).days
        return 0
    
    class Meta:
        verbose_name = 'Tarea'
        verbose_name_plural = 'Tareas'
        ordering = ['due_date', '-priority']


class TaskRequest(models.Model):
    """Solicitud de creación de tarea (cuando requiere aprobación)"""
    
    STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('approved', 'Aprobada'),
        ('rejected', 'Rechazada'),
    ]
    
    group = models.ForeignKey('groups.Group', on_delete=models.CASCADE, related_name='task_requests')
    subject = models.ForeignKey('subjects.Subject', on_delete=models.CASCADE, related_name='task_requests')
    title = models.CharField(max_length=200, verbose_name="Título")
    description = models.TextField(blank=True, verbose_name="Descripción")
    
    # Fechas
    assigned_date = models.DateField(verbose_name="Fecha mandada")
    due_date = models.DateField(verbose_name="Fecha de entrega")
    priority = models.CharField(max_length=20, choices=Task.PRIORITY_CHOICES, default='medium')
    
    # Solicitud
    requested_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='task_requests')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    message = models.TextField(blank=True, verbose_name="Mensaje/Razón")
    
    # Revisión
    reviewed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_task_requests')
    reviewed_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Solicitud de tarea: {self.subject.name} por {self.requested_by.nombre}"
    
    class Meta:
        verbose_name = 'Solicitud de Tarea'
        verbose_name_plural = 'Solicitudes de Tareas'
        ordering = ['-created_at']


def task_request_attachment_upload_to(instance, filename):
    """Genera la ruta de subida para archivos de solicitudes"""
    import os
    from django.utils.text import slugify
    
    ext = os.path.splitext(filename)[1].lower()
    safe_filename = f"{slugify(os.path.splitext(filename)[0])}{ext}"
    
    # Estructura: task_requests/group_ID/request_ID/filename
    return f"task_requests/group_{instance.task_request.group.id}/request_{instance.task_request.id}/{safe_filename}"


class TaskRequestAttachment(models.Model):
    """Archivos adjuntos temporales para solicitudes de tareas"""
    
    task_request = models.ForeignKey(TaskRequest, on_delete=models.CASCADE, related_name='temp_attachments')
    file = models.FileField(upload_to=task_request_attachment_upload_to, verbose_name="Archivo")
    
    # Metadata
    original_filename = models.CharField(max_length=255, verbose_name="Nombre original")
    file_size = models.IntegerField(verbose_name="Tamaño (bytes)")
    file_type = models.CharField(max_length=100, verbose_name="Tipo de archivo")
    
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.original_filename} - Solicitud #{self.task_request.id}"
    
    @property
    def file_size_mb(self):
        return round(self.file_size / (1024 * 1024), 2)
    
    class Meta:
        verbose_name = 'Archivo de Solicitud'
        verbose_name_plural = 'Archivos de Solicitudes'


class TaskEditRequest(models.Model):
    """Solicitud de edición de tarea (cuando requiere aprobación)"""
    
    STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('approved', 'Aprobada'),
        ('rejected', 'Rechazada'),
    ]
    
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='edit_requests')
    requested_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='task_edit_requests')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Cambios propuestos (JSON)
    proposed_changes = models.JSONField()
    message = models.TextField(blank=True, verbose_name="Mensaje/Razón")
    
    # Cambios en documentos
    documents_to_delete = models.JSONField(null=True, blank=True)  # IDs de documentos a eliminar
    
    # Revisión
    reviewed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_task_edits')
    reviewed_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Solicitud de edición: {self.task.title} por {self.requested_by.nombre}"
    
    class Meta:
        verbose_name = 'Solicitud de Edición de Tarea'
        verbose_name_plural = 'Solicitudes de Edición de Tareas'
        ordering = ['-created_at']


def task_edit_attachment_upload_to(instance, filename):
    """Genera la ruta de subida para archivos nuevos en ediciones"""
    import os
    from django.utils.text import slugify
    
    ext = os.path.splitext(filename)[1].lower()
    safe_filename = f"{slugify(os.path.splitext(filename)[0])}{ext}"
    
    # Estructura: task_edit_requests/task_ID/edit_request_ID/filename
    return f"task_edit_requests/task_{instance.edit_request.task.id}/edit_{instance.edit_request.id}/{safe_filename}"


class TaskEditAttachment(models.Model):
    """Archivos nuevos adjuntos en solicitudes de edición"""
    
    edit_request = models.ForeignKey(TaskEditRequest, on_delete=models.CASCADE, related_name='new_attachments')
    file = models.FileField(upload_to=task_edit_attachment_upload_to, verbose_name="Archivo")
    
    # Metadata
    original_filename = models.CharField(max_length=255, verbose_name="Nombre original")
    file_size = models.IntegerField(verbose_name="Tamaño (bytes)")
    file_type = models.CharField(max_length=100, verbose_name="Tipo de archivo")
    
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.original_filename} - Edición #{self.edit_request.id}"
    
    @property
    def file_size_mb(self):
        return round(self.file_size / (1024 * 1024), 2)
    
    class Meta:
        verbose_name = 'Archivo Nuevo en Edición'
        verbose_name_plural = 'Archivos Nuevos en Ediciones'


class TaskCompletion(models.Model):
    """Estado de completado de tarea por usuario (cada estudiante tiene su propio estado)"""
    
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='completions')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='task_completions')
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        status = "Completada" if self.completed else "Pendiente"
        return f"{self.user.nombre} - {self.task.title}: {status}"
    
    class Meta:
        verbose_name = 'Estado de Tarea por Usuario'
        verbose_name_plural = 'Estados de Tareas por Usuario'
        unique_together = ['task', 'user']
        ordering = ['-completed_at']



def task_attachment_upload_to(instance, filename):
    """Genera la ruta de subida para archivos adjuntos"""
    import os
    from django.utils.text import slugify
    
    # Obtener extensión del archivo
    ext = os.path.splitext(filename)[1].lower()
    
    # Generar nombre seguro
    safe_filename = f"{slugify(os.path.splitext(filename)[0])}{ext}"
    
    # Estructura: task_files/group_ID/task_ID/filename
    return f"task_files/group_{instance.task.group.id}/task_{instance.task.id}/{safe_filename}"


class TaskAttachment(models.Model):
    """Archivos adjuntos a tareas"""
    
    STATUS_CHOICES = [
        ('pending', 'Pendiente de aprobación'),
        ('approved', 'Aprobado'),
        ('rejected', 'Rechazado'),
    ]
    
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to=task_attachment_upload_to, verbose_name="Archivo")
    
    # Metadata del archivo
    original_filename = models.CharField(max_length=255, verbose_name="Nombre original")
    file_size = models.IntegerField(verbose_name="Tamaño (bytes)")
    file_type = models.CharField(max_length=100, verbose_name="Tipo de archivo")
    
    # Control de aprobación
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='approved')
    
    # Usuario
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='uploaded_attachments'
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    # Archivo físico eliminado (para tareas archivadas)
    file_deleted = models.BooleanField(default=False, verbose_name="Archivo físico eliminado")
    deleted_at = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de eliminación física")
    
    # Revisión (si requiere aprobación)
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_attachments'
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.original_filename} - {self.task.title}"
    
    @property
    def filename(self):
        """Retorna solo el nombre del archivo"""
        import os
        return os.path.basename(self.file.name)
    
    @property
    def file_size_mb(self):
        """Retorna el tamaño en MB"""
        return round(self.file_size / (1024 * 1024), 2)
    
    @property
    def is_pdf(self):
        """Verifica si es un PDF"""
        return self.file_type.lower() in ['application/pdf', 'pdf']
    
    @property
    def file_icon(self):
        """Retorna el icono apropiado según el tipo de archivo"""
        if self.is_pdf:
            return 'file-pdf'
        elif 'word' in self.file_type.lower() or self.file_type.endswith('.doc'):
            return 'file-word'
        elif 'excel' in self.file_type.lower() or self.file_type.endswith('.xls'):
            return 'file-excel'
        elif 'powerpoint' in self.file_type.lower() or self.file_type.endswith('.ppt'):
            return 'file-powerpoint'
        else:
            return 'file-text'
    
    class Meta:
        verbose_name = 'Archivo Adjunto'
        verbose_name_plural = 'Archivos Adjuntos'
        ordering = ['-uploaded_at']
