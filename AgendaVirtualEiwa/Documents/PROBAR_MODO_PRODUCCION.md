# 🧪 Cómo Probar el Modo Producción en Local

## Opción 1: Usar el Script Automático (Recomendado)

### Windows PowerShell:
```powershell
cd AgendaVirtualEiwa
.\test-production.ps1
```

### Windows CMD:
```cmd
cd AgendaVirtualEiwa
test-production.cmd
```

El script automáticamente:
1. ✅ Configura `DEBUG=False`
2. ✅ Ejecuta `collectstatic` para recolectar archivos CSS/JS
3. ✅ Inicia el servidor

---

## Opción 2: Manual (Paso a Paso)

### 1. Configurar DEBUG=False

**PowerShell:**
```powershell
$env:DEBUG = "False"
```

**CMD:**
```cmd
set DEBUG=False
```

**Linux/Mac:**
```bash
export DEBUG=False
```

### 2. Recolectar Archivos Estáticos

```bash
cd AgendaVirtualEiwa
python manage.py collectstatic --noinput
```

Verás algo como:
```
171 static files copied to 'C:\...\staticfiles'.
```

### 3. Iniciar el Servidor

```bash
python manage.py runserver
```

### 4. Probar en el Navegador

Visita: http://127.0.0.1:8000

**Verifica que:**
- ✅ Los estilos CSS se cargan correctamente
- ✅ Los archivos JavaScript funcionan
- ✅ El modo claro/oscuro funciona
- ✅ Las imágenes se muestran

### 5. Probar las Páginas de Error

Visita una URL que no existe para ver el 404:
- http://127.0.0.1:8000/pagina-que-no-existe

O usa las URLs de prueba (solo si DEBUG=True):
- http://127.0.0.1:8000/test-error/404/
- http://127.0.0.1:8000/test-error/403/
- http://127.0.0.1:8000/test-error/500/

---

## Volver al Modo Desarrollo

### Opción 1: Cerrar y Reiniciar

1. Presiona `Ctrl+C` para detener el servidor
2. Cierra la terminal
3. Abre una nueva terminal
4. Ejecuta normalmente: `python manage.py runserver`

### Opción 2: Cambiar Variable de Entorno

**PowerShell:**
```powershell
$env:DEBUG = "True"
python manage.py runserver
```

**CMD:**
```cmd
set DEBUG=True
python manage.py runserver
```

---

## ¿Qué Hace `collectstatic`?

El comando `python manage.py collectstatic` copia todos los archivos de:

```
AgendaVirtualEiwa/static/
├── css/
├── js/
└── img/
```

A:

```
AgendaVirtualEiwa/staticfiles/
├── css/
├── js/
└── img/
```

**Whitenoise** sirve los archivos desde `staticfiles/` cuando `DEBUG=False`.

---

## Diferencias entre Desarrollo y Producción

| Aspecto | Desarrollo (DEBUG=True) | Producción (DEBUG=False) |
|---------|------------------------|--------------------------|
| **Archivos estáticos** | Servidos por Django desde `static/` | Servidos por Whitenoise desde `staticfiles/` |
| **Errores** | Muestra traceback completo | Muestra páginas de error personalizadas |
| **Rendimiento** | Más lento | Optimizado y comprimido |
| **Cambios CSS/JS** | Inmediatos | Requiere `collectstatic` |

---

## Solución de Problemas

### ❌ Los CSS/JS no cargan

**Solución:**
```bash
python manage.py collectstatic --noinput
```

### ❌ Error "You're accessing the development server over HTTPS"

**Solución:** Usa `http://` en lugar de `https://`

### ❌ Las páginas de error no se muestran

**Causa:** Estás usando las URLs de prueba con DEBUG=False

**Solución:** Visita una URL que realmente no existe, como:
- http://127.0.0.1:8000/esta-pagina-no-existe

### ❌ Error "DisallowedHost"

**Solución:** Agrega `127.0.0.1` a `ALLOWED_HOSTS` en `settings.py` (ya está configurado)

---

## Comandos Útiles

```bash
# Ver qué archivos se copiarán (sin copiar)
python manage.py collectstatic --dry-run

# Limpiar archivos antiguos antes de copiar
python manage.py collectstatic --clear --noinput

# Ver configuración de despliegue
python manage.py check --deploy

# Ver todas las URLs configuradas
python manage.py show_urls  # (requiere django-extensions)
```

---

## Notas Importantes

1. 🔴 **Nunca uses DEBUG=False en desarrollo normal** - Es más lento y menos útil
2. 🟢 **Siempre ejecuta `collectstatic` antes de desplegar** - O los CSS/JS no funcionarán
3. 🟡 **La carpeta `staticfiles/` no se sube a Git** - Se genera automáticamente
4. 🔵 **Whitenoise comprime automáticamente** - Los archivos son más pequeños en producción

---

## Checklist Antes de Desplegar

- [ ] Ejecuté `collectstatic` y funcionó sin errores
- [ ] Probé con `DEBUG=False` en local y todo funciona
- [ ] Los estilos CSS se cargan correctamente
- [ ] Las páginas de error personalizadas se muestran
- [ ] No hay errores en la consola del navegador
- [ ] Las variables de entorno están configuradas en Render
- [ ] El archivo `render.yaml` incluye `collectstatic`

---

## Recursos

- [Documentación de collectstatic](https://docs.djangoproject.com/en/5.2/ref/contrib/staticfiles/#collectstatic)
- [Whitenoise](http://whitenoise.evans.io/)
- [Django Deployment Checklist](https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/)
