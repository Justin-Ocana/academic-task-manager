from django.contrib.auth.models import AbstractUser
from django.db import models
from .validators import validate_name, capitalize_name


class User(AbstractUser):
    nombre = models.CharField(
        max_length=30,
        validators=[validate_name],
        help_text="1-2 nombres, 3-30 caracteres total, solo letras"
    )
    apellido = models.CharField(
        max_length=30,
        validators=[validate_name],
        help_text="1-2 apellidos, 3-30 caracteres total, solo letras"
    )
    email = models.EmailField(unique=True)
    
    # Configuración de resumen de actividades
    RANGE_CHOICES = [
        ('today', 'Hoy'),
        ('week', 'Esta semana'),
        ('month', 'Este mes'),
        ('all', 'Todas'),
    ]
    
    pending_range = models.CharField(
        max_length=10,
        choices=RANGE_CHOICES,
        default='week',
        verbose_name='Rango de tareas pendientes'
    )
    completed_range = models.CharField(
        max_length=10,
        choices=RANGE_CHOICES,
        default='week',
        verbose_name='Rango de tareas completadas'
    )
    overdue_range = models.CharField(
        max_length=10,
        choices=[
            ('today', 'Hoy'),
            ('7days', 'Últimos 7 días'),
            ('30days', 'Últimos 30 días'),
            ('all', 'Todas'),
        ],
        default='7days',
        verbose_name='Rango de tareas vencidas'
    )
    
    # Configuración de modo multigrupo
    MULTIGROUP_MODES = [
        ('separated', 'Mantener grupos separados'),
        ('unified', 'Unificar todos los grupos'),
    ]
    
    multigroup_mode = models.CharField(
        max_length=10,
        choices=MULTIGROUP_MODES,
        default='unified',
        verbose_name='Modo de visualización multigrupo'
    )
    
    last_active_group = models.ForeignKey(
        'groups.Group',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='last_active_users',
        verbose_name='Último grupo activo'
    )
    
    # Configuración de grupos para dashboard
    dashboard_groups = models.ManyToManyField(
        'groups.Group',
        blank=True,
        related_name='dashboard_users',
        verbose_name='Grupos visibles en dashboard',
        help_text='Grupos que se mostrarán en las estadísticas del dashboard. Si está vacío, se muestran todos.'
    )
    
    # Configuración de avatar personalizado
    AVATAR_STYLES = [
        ('smile', 'Sonrisa'),
        ('cat', 'Gato'),
        ('star-eyes', 'Ojos de Estrella'),
        ('robot', 'Robot'),
        ('heart', 'Corazón'),
        ('glasses', 'Lentes'),
        ('music', 'Música'),
        ('wink', 'Guiño'),
        ('cool', 'Cool'),
        ('bear', 'Oso'),
        ('lightning', 'Rayo'),
        ('flower', 'Flor'),
        ('alien', 'Alien'),
        ('crown', 'Corona'),
        ('ninja', 'Ninja'),
        ('party', 'Fiesta'),
    ]
    
    avatar_style = models.CharField(
        max_length=20,
        choices=AVATAR_STYLES,
        null=True,
        blank=True,
        verbose_name='Estilo de avatar',
        help_text='Diseño del avatar personalizado'
    )
    avatar_bg_color = models.CharField(
        max_length=7,
        null=True,
        blank=True,
        verbose_name='Color de fondo del avatar',
        help_text='Color en formato hexadecimal (#RRGGBB)'
    )
    avatar_svg_color = models.CharField(
        max_length=7,
        null=True,
        blank=True,
        verbose_name='Color del diseño del avatar',
        help_text='Color en formato hexadecimal (#RRGGBB)'
    )
    avatar_category = models.CharField(
        max_length=20,
        default='eiwa',
        verbose_name='Categoría de avatar',
        help_text='Categoría del avatar (eiwa, animals, disney)'
    )
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'nombre', 'apellido']
    
    def save(self, *args, **kwargs):
        # Capitalizar automáticamente nombre y apellido
        if self.nombre:
            self.nombre = capitalize_name(self.nombre.strip())
        if self.apellido:
            self.apellido = capitalize_name(self.apellido.strip())
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.nombre} {self.apellido}"
    
    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'

