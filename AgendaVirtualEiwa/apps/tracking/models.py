from django.db import models
from django.conf import settings
from apps.groups.models import Group
from apps.tasks.models import Task


class TaskHistory(models.Model):
    """Historial de cambios en tareas"""
    ACTION_CHOICES = [
        ('created', 'Creada'),
        ('edited', 'Editada'),
        ('deleted', 'Eliminada'),
        ('completed', 'Completada'),
        ('reopened', 'Reabierta'),
    ]
    
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='history', null=True, blank=True)
    task_title = models.CharField(max_length=200)  # Guardar título por si se elimina
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='task_history')
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    # Campos para guardar cambios
    field_changed = models.CharField(max_length=100, blank=True)
    old_value = models.TextField(blank=True)
    new_value = models.TextField(blank=True)
    
    # Datos adicionales en JSON
    details = models.JSONField(default=dict, blank=True)
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Historial de Tarea'
        verbose_name_plural = 'Historial de Tareas'
    
    def __str__(self):
        return f"{self.task_title} - {self.get_action_display()} por {self.user}"


class GroupActivity(models.Model):
    """Actividad y cambios en grupos"""
    ACTION_CHOICES = [
        ('member_joined', 'Miembro se unió'),
        ('member_left', 'Miembro salió'),
        ('member_removed', 'Miembro expulsado'),
        ('member_approved', 'Miembro aprobado'),
        ('member_rejected', 'Solicitud rechazada'),
        ('role_changed', 'Rol cambiado'),
        ('permissions_changed', 'Permisos modificados'),
        ('group_created', 'Grupo creado'),
        ('group_updated', 'Grupo actualizado'),
        ('subject_added', 'Materia agregada'),
        ('subject_removed', 'Materia eliminada'),
    ]
    
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='activity_log')
    action = models.CharField(max_length=30, choices=ACTION_CHOICES)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='group_actions')
    affected_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='affected_by_actions')
    timestamp = models.DateTimeField(auto_now_add=True)
    
    # Detalles del cambio
    description = models.TextField(blank=True)
    details = models.JSONField(default=dict, blank=True)
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Actividad de Grupo'
        verbose_name_plural = 'Actividades de Grupo'
    
    def __str__(self):
        return f"{self.group.name} - {self.get_action_display()}"


class UserActionLog(models.Model):
    """Log general de acciones de usuarios (para auditoría)"""
    ACTION_TYPES = [
        ('login', 'Inicio de sesión'),
        ('logout', 'Cierre de sesión'),
        ('task_create', 'Crear tarea'),
        ('task_edit', 'Editar tarea'),
        ('task_delete', 'Eliminar tarea'),
        ('task_complete', 'Completar tarea'),
        ('group_create', 'Crear grupo'),
        ('group_join', 'Unirse a grupo'),
        ('group_leave', 'Salir de grupo'),
        ('subject_create', 'Crear materia'),
        ('subject_delete', 'Eliminar materia'),
        ('permission_change', 'Cambiar permisos'),
        ('member_remove', 'Expulsar miembro'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    action_type = models.CharField(max_length=30, choices=ACTION_TYPES)
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=255, blank=True)
    
    # Referencias opcionales
    group = models.ForeignKey(Group, on_delete=models.SET_NULL, null=True, blank=True)
    task = models.ForeignKey(Task, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Detalles adicionales
    details = models.JSONField(default=dict, blank=True)
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Log de Acción'
        verbose_name_plural = 'Logs de Acciones'
    
    def __str__(self):
        return f"{self.user} - {self.get_action_type_display()} - {self.timestamp}"


class RevertibleAction(models.Model):
    """Acciones que pueden ser revertidas"""
    ACTION_TYPES = [
        ('task_edit', 'Edición de tarea'),
        ('task_delete', 'Eliminación de tarea'),
        ('member_remove', 'Expulsión de miembro'),
        ('permission_change', 'Cambio de permisos'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Activa'),
        ('reverted', 'Revertida'),
        ('expired', 'Expirada'),
    ]
    
    action_type = models.CharField(max_length=30, choices=ACTION_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    performed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='performed_actions')
    reverted_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='reverted_actions')
    
    timestamp = models.DateTimeField(auto_now_add=True)
    reverted_at = models.DateTimeField(null=True, blank=True)
    
    # Datos para revertir
    snapshot_data = models.JSONField()  # Estado antes del cambio
    
    # Referencias
    task = models.ForeignKey(Task, on_delete=models.SET_NULL, null=True, blank=True)
    affected_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='affected_actions')
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Acción Revertible'
        verbose_name_plural = 'Acciones Revertibles'
    
    def __str__(self):
        return f"{self.get_action_type_display()} - {self.status}"
