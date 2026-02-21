from django.db import models
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


class Notification(models.Model):
    """Modelo de notificaciones para usuarios"""
    
    NOTIFICATION_TYPES = [
        ('group_invite', 'Invitación a Grupo'),
        ('join_request', 'Solicitud de Ingreso'),
        ('request_approved', 'Solicitud Aprobada'),
        ('request_rejected', 'Solicitud Rechazada'),
        ('member_promoted', 'Promoción de Rol'),
        ('member_demoted', 'Degradación de Rol'),
        ('member_removed', 'Expulsado del Grupo'),
        ('member_banned', 'Baneado del Grupo'),
        ('member_unbanned', 'Desbaneado del Grupo'),
        ('task_assigned', 'Tarea Asignada'),
        ('task_completed', 'Tarea Completada'),
        ('task_reminder', 'Recordatorio de Tarea'),
        ('event_reminder', 'Recordatorio de Evento'),
        ('subject_added', 'Materia Agregada'),
        ('general', 'General'),
    ]
    
    # Usuario que recibe la notificación
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    
    # Usuario que genera la notificación (opcional)
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sent_notifications'
    )
    
    # Tipo de notificación
    notification_type = models.CharField(max_length=30, choices=NOTIFICATION_TYPES)
    
    # Contenido
    title = models.CharField(max_length=200)
    message = models.TextField()
    
    # Objeto relacionado (genérico)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    
    # URL de acción (opcional)
    action_url = models.CharField(max_length=500, blank=True)
    
    # Estado
    is_read = models.BooleanField(default=False)
    is_seen = models.BooleanField(default=False)  # Visto en el dropdown
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.recipient.nombre} - {self.title}"
    
    class Meta:
        verbose_name = 'Notificación'
        verbose_name_plural = 'Notificaciones'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient', '-created_at']),
            models.Index(fields=['recipient', 'is_read']),
        ]
