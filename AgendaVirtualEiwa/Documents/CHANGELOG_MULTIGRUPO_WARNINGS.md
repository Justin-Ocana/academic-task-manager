# Changelog: Sistema de Advertencias Multigrupo

## Fecha: 2026-02-04

## Cambios Implementados

### 1. Modal de Advertencia al Crear/Unirse a un Segundo Grupo

#### Archivos Modificados:
- `AgendaVirtualEiwa/apps/groups/templates/groups/create_group.html`
- `AgendaVirtualEiwa/apps/groups/templates/groups/join_group.html`
- `AgendaVirtualEiwa/apps/groups/views.py`

#### Funcionalidad:
- Se agregó un modal de advertencia que aparece cuando un usuario intenta crear o unirse a un segundo grupo
- El modal informa que los multigrupos están en fase experimental
- Recomienda estar en un solo grupo para una experiencia óptima
- Advierte sobre posibles errores y comportamientos inesperados
- El usuario puede cancelar o continuar bajo su propio riesgo

#### Implementación:
```html
<!-- Modal con diseño atractivo -->
- Icono de advertencia en amarillo/naranja
- Título "Función Experimental"
- Mensaje claro sobre el estado experimental
- Caja de advertencia destacada
- Botones: "Cancelar" y "Entiendo, Continuar"
```

#### JavaScript:
```javascript
- Detecta si el usuario ya tiene 1 o más grupos
- Intercepta el submit del formulario
- Muestra el modal antes de enviar
- Solo permite enviar después de confirmar
```

#### Vistas Actualizadas:
```python
# create_group y join_group
- Se agregó contador de grupos del usuario: user_groups_count
- Se pasa al template para controlar la visualización del modal
```

---

### 2. Deshabilitar Opciones Multigrupo en Settings

#### Archivos Modificados:
- `AgendaVirtualEiwa/apps/core/templates/settings/profile_settings.html`
- `AgendaVirtualEiwa/static/css/profile-settings.css`

#### Funcionalidad:
Las siguientes secciones se deshabilitan cuando el usuario tiene menos de 2 grupos:

1. **Visualización Multigrupo**
   - Radio buttons deshabilitados
   - Formulario con opacidad reducida y sin interacción
   - Mensaje informativo visible

2. **Grupos del Dashboard**
   - Checkboxes deshabilitados
   - Formulario con opacidad reducida y sin interacción
   - Mensaje informativo visible

#### Mensaje Informativo:
```
⚠️ Necesitas pertenecer a 2 o más grupos para usar esta función.
Actualmente estás en X grupo(s). Crea o únete a otro grupo para habilitar [función].
```

#### Estilos CSS Agregados:
```css
.settings-card.disabled-section {
    /* Overlay semi-transparente con blur */
}

.feature-disabled-notice {
    /* Caja de aviso amarilla con borde naranja */
    /* Diseño atractivo y claro */
}

.btn-primary:disabled, .btn-secondary:disabled {
    /* Botones deshabilitados con cursor not-allowed */
}
```

#### Lógica de Deshabilitación:
```django
{% if user_groups|length < 2 %}
    <!-- Agregar clase disabled-section -->
    <!-- Mostrar mensaje informativo -->
    <!-- Deshabilitar inputs y botones -->
    <!-- Aplicar estilos de opacidad -->
{% endif %}
```

---

## Flujo de Usuario

### Escenario 1: Usuario con 0 grupos
1. Crea su primer grupo → Sin advertencia
2. El grupo se agrega automáticamente a dashboard_groups
3. En settings, las opciones multigrupo están deshabilitadas

### Escenario 2: Usuario con 1 grupo
1. Intenta crear/unirse a un segundo grupo → **Modal de advertencia**
2. Puede cancelar o continuar
3. Si continúa, se une al segundo grupo
4. En settings, las opciones multigrupo se habilitan automáticamente

### Escenario 3: Usuario con 2+ grupos
1. Puede crear/unirse a más grupos → **Modal de advertencia** en cada intento
2. En settings, todas las opciones multigrupo están habilitadas
3. Puede configurar visualización y grupos del dashboard libremente

---

## Beneficios

1. **Transparencia**: Los usuarios saben que los multigrupos son experimentales
2. **Prevención**: Se desalienta el uso de múltiples grupos
3. **Flexibilidad**: Los usuarios pueden probar la función si lo desean
4. **UX Mejorada**: Las opciones no disponibles están claramente deshabilitadas
5. **Guía Clara**: Mensajes informativos explican cómo habilitar las funciones

---

## Notas Técnicas

- El contador de grupos se calcula en tiempo real en las vistas
- Los modales usan JavaScript vanilla (sin dependencias)
- Los estilos son consistentes con el diseño de la aplicación
- La lógica de deshabilitación es puramente visual (no afecta la seguridad)
- Las validaciones del lado del servidor permanecen intactas

---

## Testing Recomendado

1. Crear primer grupo → Verificar que no aparece modal
2. Intentar crear segundo grupo → Verificar modal de advertencia
3. Cancelar en el modal → Verificar que no se crea el grupo
4. Confirmar en el modal → Verificar que se crea el grupo
5. Con 1 grupo, ir a settings → Verificar opciones deshabilitadas
6. Con 2+ grupos, ir a settings → Verificar opciones habilitadas
7. Intentar unirse a un grupo con código → Verificar modal si ya tiene 1+
