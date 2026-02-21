from django.db import models
from django.conf import settings
from apps.accounts.validators import validate_subject_name
import random


class Subject(models.Model):
    """Modelo de Materia"""
    
    COLOR_CHOICES = [
        ('#006DB9', 'Azul Principal'),
        ('#87A9E0', 'Azul Pastel'),
        ('#003366', 'Azul Secundario'),
        ('#FF8C00', 'Naranja EIWA'),
        ('#FFB84D', 'Naranja Pastel'),
        ('#28a745', 'Verde'),
        ('#dc3545', 'Rojo'),
        ('#6f42c1', 'Morado'),
        ('#fd7e14', 'Naranja'),
        ('#20c997', 'Verde Agua'),
        ('#e83e8c', 'Rosa'),
        ('#17a2b8', 'Cyan'),
    ]
    
    group = models.ForeignKey('groups.Group', on_delete=models.CASCADE, related_name='subjects')
    name = models.CharField(
        max_length=40,
        verbose_name="Nombre de la materia",
        validators=[validate_subject_name],
        help_text="2-40 caracteres, letras, números y guiones"
    )
    color = models.CharField(max_length=7, choices=COLOR_CHOICES, default='#006DB9')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='created_subjects')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} - {self.group.name}"
    
    def save(self, *args, **kwargs):
        # Si no se especifica color, asignar uno aleatorio
        if not self.color:
            self.color = random.choice([c[0] for c in self.COLOR_CHOICES])
        super().save(*args, **kwargs)
    
    class Meta:
        verbose_name = 'Materia'
        verbose_name_plural = 'Materias'
        unique_together = ['group', 'name']
        ordering = ['name']


class SubjectRequest(models.Model):
    """Solicitudes para agregar materias (cuando requiere aprobación)"""
    
    COLOR_CHOICES = [
        ('#006DB9', 'Azul Principal'),
        ('#87A9E0', 'Azul Pastel'),
        ('#003366', 'Azul Secundario'),
        ('#FF8C00', 'Naranja EIWA'),
        ('#FFB84D', 'Naranja Pastel'),
        ('#28a745', 'Verde'),
        ('#dc3545', 'Rojo'),
        ('#6f42c1', 'Morado'),
        ('#fd7e14', 'Naranja'),
        ('#20c997', 'Verde Agua'),
        ('#e83e8c', 'Rosa'),
        ('#17a2b8', 'Cyan'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('approved', 'Aprobada'),
        ('rejected', 'Rechazada'),
    ]
    
    group = models.ForeignKey('groups.Group', on_delete=models.CASCADE, related_name='subject_requests')
    name = models.CharField(
        max_length=40,
        verbose_name="Nombre de la materia",
        validators=[validate_subject_name],
        help_text="2-40 caracteres, letras, números y guiones"
    )
    color = models.CharField(max_length=7, choices=COLOR_CHOICES, default='#006DB9')
    requested_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='subject_requests')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_subject_requests'
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.name} - {self.group.name} ({self.get_status_display()})"
    
    class Meta:
        verbose_name = 'Solicitud de Materia'
        verbose_name_plural = 'Solicitudes de Materias'
        ordering = ['-created_at']

