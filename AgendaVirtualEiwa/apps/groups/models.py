from django.db import models
from django.conf import settings
from django.utils.crypto import get_random_string
import uuid


class Group(models.Model):
    """Modelo principal de Grupo/Curso"""
    
    # Información básica
    name = models.CharField(max_length=200, verbose_name="Nombre del grupo")
    description = models.TextField(blank=True, verbose_name="Descripción")
    max_members = models.IntegerField(default=50, verbose_name="Máximo de estudiantes")
    invite_code = models.CharField(max_length=10, unique=True, verbose_name="Código de invitación")
    
    # Configuración de ingreso
    ENTRY_TYPES = [
        ('free', 'Ingreso Libre'),
        ('approval', 'Ingreso con Aprobación'),
    ]
    entry_type = models.CharField(max_length=20, choices=ENTRY_TYPES, default='approval')
    is_invite_active = models.BooleanField(default=True, verbose_name="Código activo")
    
    # Permisos de tareas
    TASK_CREATE_PERMISSIONS = [
        ('all', 'Todos pueden crear'),
        ('leader', 'Solo líder'),
        ('approval', 'Todos, pero requiere aprobación'),
    ]
    task_create_permission = models.CharField(max_length=20, choices=TASK_CREATE_PERMISSIONS, default='all')
    
    TASK_EDIT_PERMISSIONS = [
        ('all', 'Todos pueden editar'),
        ('leader', 'Solo líder'),
        ('approval', 'Editar requiere aprobación del líder'),
        ('approval_leader_creator', 'Editar requiere aprobación del líder o creador'),
    ]
    task_edit_permission = models.CharField(max_length=30, choices=TASK_EDIT_PERMISSIONS, default='leader')
    
    TASK_DELETE_PERMISSIONS = [
        ('leader', 'Solo líder'),
        ('leader_creator', 'Líder + creador'),
        ('all', 'Cualquiera'),
    ]
    task_delete_permission = models.CharField(max_length=20, choices=TASK_DELETE_PERMISSIONS, default='leader')
    
    TASK_REVERT_PERMISSIONS = [
        ('leader', 'Solo líder'),
        ('leader_creator', 'Líder + creador original'),
    ]
    task_revert_permission = models.CharField(max_length=20, choices=TASK_REVERT_PERMISSIONS, default='leader')
    
    # Permisos de materias
    SUBJECT_PERMISSIONS = [
        ('leader', 'Solo líder'),
        ('suggest', 'Sugerir (requiere aprobación)'),
        ('all', 'Todos pueden crear'),
    ]
    subject_permission = models.CharField(max_length=20, choices=SUBJECT_PERMISSIONS, default='leader')
    
    # Moderación de contenido
    CONTENT_MODERATION_MODES = [
        ('off', 'Desactivada'),
        ('censor', 'Censurar palabras (###)'),
        ('block', 'Bloquear contenido'),
    ]
    content_moderation = models.CharField(
        max_length=20, 
        choices=CONTENT_MODERATION_MODES, 
        default='censor',
        verbose_name="Moderación de contenido"
    )
    
    # Configuración de documentos
    documents_enabled = models.BooleanField(default=False, verbose_name="Habilitar documentos")
    
    DOCUMENT_UPLOAD_PERMISSIONS = [
        ('all', 'Todos pueden subir'),
        ('leader', 'Solo líder'),
        ('approval', 'Todos, pero requiere aprobación'),
    ]
    document_upload_permission = models.CharField(
        max_length=20, 
        choices=DOCUMENT_UPLOAD_PERMISSIONS, 
        default='all',
        verbose_name="Permisos de subida de documentos"
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    def generate_invite_code(self):
        """Genera un código de invitación único"""
        while True:
            code = get_random_string(8, allowed_chars='ABCDEFGHJKLMNPQRSTUVWXYZ23456789')
            if not Group.objects.filter(invite_code=code).exists():
                return code
    
    def save(self, *args, **kwargs):
        if not self.invite_code:
            self.invite_code = self.generate_invite_code()
        super().save(*args, **kwargs)
    
    class Meta:
        verbose_name = 'Grupo'
        verbose_name_plural = 'Grupos'
        ordering = ['-created_at']


class GroupMember(models.Model):
    """Miembros del grupo con sus roles"""
    
    ROLES = [
        ('leader', 'Líder'),
        ('co_leader', 'Co-líder'),
        ('member', 'Miembro'),
    ]
    
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='members')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='group_memberships')
    role = models.CharField(max_length=20, choices=ROLES, default='member')
    warnings = models.IntegerField(default=0, verbose_name="Advertencias")
    joined_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.nombre} - {self.group.name} ({self.get_role_display()})"
    
    class Meta:
        verbose_name = 'Miembro de Grupo'
        verbose_name_plural = 'Miembros de Grupos'
        unique_together = ['group', 'user']
        ordering = ['role', '-joined_at']


class JoinRequest(models.Model):
    """Solicitudes para unirse a un grupo"""
    
    STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('approved', 'Aprobada'),
        ('rejected', 'Rechazada'),
    ]
    
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='join_requests')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='join_requests')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    message = models.TextField(blank=True, verbose_name="Mensaje opcional")
    created_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='reviewed_requests'
    )
    
    def __str__(self):
        return f"{self.user.nombre} -> {self.group.name} ({self.get_status_display()})"
    
    class Meta:
        verbose_name = 'Solicitud de Ingreso'
        verbose_name_plural = 'Solicitudes de Ingreso'
        unique_together = ['group', 'user']
        ordering = ['-created_at']


class BannedUser(models.Model):
    """Usuarios baneados de un grupo"""
    
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='banned_users')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='banned_from_groups')
    reason = models.TextField(blank=True, verbose_name="Razón del baneo")
    banned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='banned_users'
    )
    banned_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.nombre} baneado de {self.group.name}"
    
    class Meta:
        verbose_name = 'Usuario Baneado'
        verbose_name_plural = 'Usuarios Baneados'
        unique_together = ['group', 'user']
        ordering = ['-banned_at']


class GroupActivity(models.Model):
    """Historial de actividades del grupo"""
    
    ACTIVITY_TYPES = [
        ('group_created', 'Grupo creado'),
        ('member_joined', 'Miembro se unió'),
        ('member_left', 'Miembro salió'),
        ('member_removed', 'Miembro expulsado'),
        ('member_banned', 'Miembro baneado'),
        ('member_unbanned', 'Miembro desbaneado'),
        ('member_warned', 'Advertencia dada'),
        ('role_changed', 'Rol cambiado'),
        ('settings_changed', 'Configuración cambiada'),
        ('invite_regenerated', 'Código regenerado'),
        ('task_created', 'Tarea creada'),
        ('task_edited', 'Tarea editada'),
        ('task_deleted', 'Tarea eliminada'),
        ('task_reverted', 'Cambio revertido'),
        ('subject_created', 'Materia creada'),
        ('subject_deleted', 'Materia eliminada'),
    ]
    
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='activities')
    activity_type = models.CharField(max_length=30, choices=ACTIVITY_TYPES)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='group_activities')
    target_user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='targeted_activities'
    )
    description = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.group.name} - {self.get_activity_type_display()}"
    
    class Meta:
        verbose_name = 'Actividad de Grupo'
        verbose_name_plural = 'Actividades de Grupos'
        ordering = ['-created_at']
