# Configuración de Páginas de Error Personalizadas

## Archivos Creados

Se han creado 3 páginas de error personalizadas con el estilo de la plataforma:

- `AgendaVirtualEiwa/templates/404.html` - Página no encontrada
- `AgendaVirtualEiwa/templates/403.html` - Acceso denegado
- `AgendaVirtualEiwa/templates/500.html` - Error del servidor

## Características

✅ **Diseño consistente** con la identidad visual de Agenda Virtual Eiwa
✅ **Modo claro y oscuro** - Se adapta automáticamente al tema guardado del usuario
✅ **Responsive** - Funciona perfectamente en móviles y tablets
✅ **Animaciones suaves** - Transiciones y efectos visuales profesionales
✅ **Botones de acción** - Ir al inicio, volver atrás, reintentar
✅ **Toggle de tema** - Botón flotante para cambiar entre modo claro/oscuro

## Configuración en Django

### 1. Verificar que DEBUG esté en False en producción

En `AgendaVirtualEiwa/settings.py`, asegúrate de que en producción:

```python
DEBUG = False
```

### 2. Configurar ALLOWED_HOSTS

En `AgendaVirtualEiwa/settings.py`:

```python
ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    '.onrender.com',
    'tu-dominio.com',  # Agrega tu dominio si tienes uno
]
```

### 3. Las páginas de error se activan automáticamente

Django busca automáticamente estos archivos en la carpeta `templates/`:
- `404.html` - Cuando una URL no existe
- `403.html` - Cuando el usuario no tiene permisos
- `500.html` - Cuando hay un error del servidor

## Probar las Páginas de Error

### En desarrollo (con DEBUG=True):

Para probar las páginas de error en desarrollo, puedes:

1. **Crear vistas de prueba** en `urls.py`:

```python
from django.urls import path
from django.views.generic import TemplateView

urlpatterns = [
    # ... tus URLs existentes
    
    # URLs de prueba para páginas de error (solo en desarrollo)
    path('test-404/', TemplateView.as_view(template_name='404.html')),
    path('test-403/', TemplateView.as_view(template_name='403.html')),
    path('test-500/', TemplateView.as_view(template_name='500.html')),
]
```

2. **Temporalmente cambiar DEBUG a False**:
   - En `settings.py` cambia `DEBUG = False`
   - Visita una URL que no existe para ver el 404
   - Recuerda volver a poner `DEBUG = True` después

### En producción (con DEBUG=False):

Las páginas se mostrarán automáticamente cuando ocurran errores.

## Personalización

### Cambiar colores

Los colores están definidos en las variables CSS al inicio de cada archivo:

```css
:root {
    --azul-principal: #006DB9;
    --azul-secundario: #006DB9;
    --azul-pastel: #87A9E0;
    --naranja-eiwa: #F6AD19;
    --naranja-pastel: #FDD28C;
}
```

### Cambiar mensajes

Puedes editar los textos en cada archivo HTML:

- **404.html**: "Página no encontrada"
- **403.html**: "Acceso Denegado"
- **500.html**: "Error del Servidor"

### Cambiar iconos

Los iconos son SVG inline. Puedes reemplazarlos con otros iconos de tu preferencia.

## Logging de Errores 500

Para recibir notificaciones de errores 500 en producción, configura en `settings.py`:

```python
# Configuración de logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'django_errors.log',
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
        }
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    },
}

# Configurar ADMINS para recibir emails de errores
ADMINS = [
    ('Tu Nombre', 'tu-email@ejemplo.com'),
]
```

## Notas Importantes

1. **Las páginas de error solo funcionan con DEBUG=False**
2. **El tema (claro/oscuro) se sincroniza con el localStorage del usuario**
3. **Las páginas son completamente independientes** - no requieren autenticación ni sesión
4. **Son páginas estáticas** - no tienen acceso al contexto de Django por seguridad

## Estructura de Archivos

```
AgendaVirtualEiwa/
├── templates/
│   ├── 404.html  ← Página no encontrada
│   ├── 403.html  ← Acceso denegado
│   └── 500.html  ← Error del servidor
└── AgendaVirtualEiwa/
    └── settings.py  ← Configuración de Django
```

## Soporte

Si necesitas ayuda o quieres personalizar más las páginas de error, consulta la documentación de Django:
https://docs.djangoproject.com/en/5.2/topics/http/views/#customizing-error-views
