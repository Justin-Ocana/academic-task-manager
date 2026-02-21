# Guía de Despliegue a Producción

## Configuración Actual

El proyecto está configurado para funcionar automáticamente en desarrollo y producción:

- **Desarrollo**: `DEBUG=True` (por defecto)
- **Producción**: `DEBUG=False` (configurado con variable de entorno)

## Pasos para Desplegar en Render.com

### 1. Recolectar Archivos Estáticos

Antes de desplegar, ejecuta:

```bash
python manage.py collectstatic --noinput
```

Este comando:
- Copia todos los archivos CSS, JS e imágenes a la carpeta `staticfiles/`
- Whitenoise los comprimirá y servirá en producción
- Los archivos se optimizan automáticamente

### 2. Configurar Variables de Entorno en Render

En el dashboard de Render, configura estas variables:

```
DEBUG=False
SECRET_KEY=tu-clave-secreta-super-segura-aqui
DATABASE_URL=tu-url-de-base-de-datos
RENDER_EXTERNAL_HOSTNAME=tu-app.onrender.com
```

### 3. Verificar render.yaml

Tu archivo `render.yaml` debe incluir el comando `collectstatic`:

```yaml
services:
  - type: web
    name: agenda-virtual-eiwa
    env: python
    buildCommand: |
      pip install -r requirements.txt
      python manage.py collectstatic --noinput
      python manage.py migrate
    startCommand: gunicorn AgendaVirtualEiwa.wsgi:application
```

## Cómo Funcionan los Archivos Estáticos

### En Desarrollo (DEBUG=True)
- Django sirve los archivos directamente desde `AgendaVirtualEiwa/static/`
- No necesitas ejecutar `collectstatic`
- Los cambios en CSS/JS se reflejan inmediatamente

### En Producción (DEBUG=False)
- Whitenoise sirve los archivos desde `staticfiles/`
- Los archivos se comprimen y optimizan automáticamente
- Debes ejecutar `collectstatic` cada vez que cambies CSS/JS

## Páginas de Error Personalizadas

Las páginas de error funcionan automáticamente:

### En Desarrollo (DEBUG=True)
- Puedes probarlas en:
  - http://localhost:8000/test-error/404/
  - http://localhost:8000/test-error/403/
  - http://localhost:8000/test-error/500/

### En Producción (DEBUG=False)
- Se muestran automáticamente cuando ocurren errores reales
- Django busca los templates en `AgendaVirtualEiwa/templates/`:
  - `404.html` - Página no encontrada
  - `403.html` - Acceso denegado
  - `500.html` - Error del servidor

## Verificar que Todo Funciona

### Antes de Desplegar

1. **Probar con DEBUG=False localmente**:
   ```bash
   # En tu terminal, configura la variable de entorno
   set DEBUG=False  # Windows CMD
   $env:DEBUG="False"  # Windows PowerShell
   export DEBUG=False  # Linux/Mac
   
   # Recolecta archivos estáticos
   python manage.py collectstatic --noinput
   
   # Inicia el servidor
   python manage.py runserver
   ```

2. **Verifica que**:
   - Los archivos CSS/JS cargan correctamente
   - Las páginas de error se muestran (visita una URL que no existe)
   - El sitio funciona normalmente

3. **Vuelve a DEBUG=True**:
   ```bash
   set DEBUG=True  # Windows CMD
   $env:DEBUG="True"  # Windows PowerShell
   export DEBUG=True  # Linux/Mac
   ```

### Después de Desplegar

1. Visita tu sitio en Render
2. Verifica que los estilos se carguen correctamente
3. Prueba una URL que no existe para ver el 404 personalizado
4. Revisa los logs en Render si algo falla

## Solución de Problemas

### Los CSS/JS no cargan en producción

1. Verifica que ejecutaste `collectstatic`:
   ```bash
   python manage.py collectstatic --noinput
   ```

2. Verifica que Whitenoise esté en `MIDDLEWARE` (ya está configurado):
   ```python
   MIDDLEWARE = [
       'django.middleware.security.SecurityMiddleware',
       'whitenoise.middleware.WhiteNoiseMiddleware',  # ← Debe estar aquí
       ...
   ]
   ```

3. Verifica los logs de Render para ver errores

### Las páginas de error no se muestran

1. Verifica que `DEBUG=False` en producción
2. Verifica que los templates existan en `AgendaVirtualEiwa/templates/`
3. Verifica que `TEMPLATES['DIRS']` incluya la carpeta templates (ya está configurado)

### Error "DisallowedHost"

Agrega tu dominio a `ALLOWED_HOSTS` en `settings.py`:
```python
ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    '.onrender.com',
    'tu-dominio-personalizado.com',  # Si tienes uno
]
```

## Comandos Útiles

```bash
# Recolectar archivos estáticos
python manage.py collectstatic --noinput

# Ver qué archivos se recolectaron
python manage.py collectstatic --noinput --dry-run

# Limpiar archivos estáticos antiguos
python manage.py collectstatic --noinput --clear

# Verificar configuración
python manage.py check --deploy
```

## Estructura de Archivos Estáticos

```
AgendaVirtualEiwa/
├── static/                    # Archivos fuente (desarrollo)
│   ├── css/
│   ├── js/
│   └── img/
├── staticfiles/              # Archivos recolectados (producción)
│   └── (generado por collectstatic)
└── templates/                # Templates de error
    ├── 404.html
    ├── 403.html
    └── 500.html
```

## Notas Importantes

1. **Nunca subas `staticfiles/` a Git** - Se genera automáticamente
2. **Ejecuta `collectstatic` antes de cada despliegue**
3. **Las páginas de error solo funcionan con DEBUG=False**
4. **Whitenoise maneja todo automáticamente en producción**

## Recursos

- [Documentación de Whitenoise](http://whitenoise.evans.io/)
- [Django Static Files](https://docs.djangoproject.com/en/5.2/howto/static-files/)
- [Django Error Views](https://docs.djangoproject.com/en/5.2/topics/http/views/#customizing-error-views)
