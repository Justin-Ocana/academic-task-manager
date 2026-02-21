# Fix - Mostrar Descripción en Solicitudes de Edición con Solo Documentos

## Fecha: 6 de febrero de 2026

## Problema Identificado

Cuando un usuario editaba una tarea y solo agregaba archivos (sin cambiar texto, fechas, etc.), la solicitud de edición mostraba:

```
Cambios propuestos
ℹ️ Sin cambios específicos - Solicitud de revisión
```

Esto era confuso para el líder porque no sabía:
- De qué tarea se trataba
- Cuál era la descripción actual
- Qué contenido tenía la tarea

## Solución Implementada

Ahora, cuando no hay cambios en los campos de texto pero sí hay cambios en documentos, se muestra:

```
Cambios propuestos
ℹ️ Sin cambios en los campos de texto

Información de la tarea:
Materia: Filosofía - Historia
Descripción: Resolver ejercicios del 1 al 10...
Fecha de entrega: 15/02/2026
```

## Cambios Realizados

### 1. Template Modificado

**Archivo:** `AgendaVirtualEiwa/apps/core/templates/requests/group_requests.html`

**Antes:**
```html
{% else %}
<div class="no-changes">
    <svg>...</svg>
    <p>Sin cambios específicos - Solicitud de revisión</p>
</div>
{% endif %}
```

**Después:**
```html
{% else %}
<div class="no-changes">
    <svg>...</svg>
    <p>Sin cambios en los campos de texto</p>
</div>

<!-- Mostrar información actual de la tarea -->
<div class="current-task-info">
    <div class="info-label">Información de la tarea:</div>
    <div class="info-item">
        <strong>Materia:</strong> {{ req.task.subject.name }}
    </div>
    <div class="info-item">
        <strong>Descripción:</strong> {{ req.task.description|default:"Sin descripción" }}
    </div>
    <div class="info-item">
        <strong>Fecha de entrega:</strong> {{ req.task.due_date|date:"d/m/Y" }}
    </div>
</div>
{% endif %}
```

### 2. Estilos CSS Agregados

**Archivo:** `AgendaVirtualEiwa/static/css/requests.css`

Se agregaron estilos para `.current-task-info`:
- Fondo azul claro con gradiente
- Borde azul
- Diseño limpio y organizado
- Soporte completo para modo oscuro
- Responsive

## Beneficios

1. **Contexto claro:** El líder ve inmediatamente de qué tarea se trata
2. **Información completa:** Muestra materia, descripción y fecha
3. **Menos confusión:** Ya no dice "sin cambios específicos"
4. **Mejor UX:** El líder puede tomar decisiones informadas

## Casos de Uso

### Caso 1: Solo agregar documentos
**Antes:**
- Usuario edita tarea
- Adjunta 1 archivo
- Líder ve: "Sin cambios específicos - Solicitud de revisión"
- ❌ No sabe de qué tarea se trata

**Ahora:**
- Usuario edita tarea
- Adjunta 1 archivo
- Líder ve: "Sin cambios en los campos de texto" + información de la tarea
- ✅ Sabe exactamente de qué tarea se trata

### Caso 2: Cambiar texto Y agregar documentos
- Se muestran los cambios de texto normalmente
- NO se muestra la sección de información (no es necesaria)
- Los documentos se muestran en "Cambios en documentos"

### Caso 3: Solo cambiar texto (sin documentos)
- Se muestran los cambios de texto normalmente
- NO se muestra la sección de información (no es necesaria)
- NO hay sección de "Cambios en documentos"

## Visualización

### Antes:
```
┌─────────────────────────────────────────┐
│ Cambios propuestos                      │
├─────────────────────────────────────────┤
│ ℹ️  Sin cambios específicos -           │
│    Solicitud de revisión                │
└─────────────────────────────────────────┘
```

### Ahora (Diseño Profesional):
```
┌─────────────────────────────────────────┐
│ Cambios propuestos                      │
├─────────────────────────────────────────┤
│ 📋 INFORMACIÓN DE LA TAREA              │
├─────────────────────────────────────────┤
│ ┌──────────────┐  ┌──────────────┐     │
│ │ 📚 MATERIA   │  │ 📅 FECHA     │     │
│ │ Filosofía -  │  │ 15/02/2026   │     │
│ │ Historia     │  │              │     │
│ └──────────────┘  └──────────────┘     │
│                                         │
│ ━━ DESCRIPCIÓN ━━━━━━━━━━━━━━━━━━━━━  │
│ │ Resolver ejercicios del 1 al 10     │ │
│ │ de la página 45...                  │ │
│ └─────────────────────────────────────┘ │
└─────────────────────────────────────────┘
│                                         │
│ Cambios en documentos                   │
├─────────────────────────────────────────┤
│ + Documentos a agregar:                 │
│   📄 archivo.pdf (362.4 KB)             │
└─────────────────────────────────────────┘
```

**Características del nuevo diseño:**
- ✨ Header con gradiente azul y icono
- 📊 Grid de tarjetas para materia y fecha
- 🎨 Iconos visuales para cada campo
- 📝 Descripción en tarjeta separada con borde destacado
- 🌙 Soporte completo para modo oscuro
- 📱 Totalmente responsive
- 🎯 Diseño limpio y profesional

## Pruebas Recomendadas

1. ✅ Editar tarea solo agregando archivos
2. ✅ Verificar que se muestre la información de la tarea
3. ✅ Verificar que se vea bien en modo oscuro
4. ✅ Verificar que sea responsive en móvil
5. ✅ Editar tarea cambiando texto (no debe mostrar info extra)

## Archivos Modificados

1. `AgendaVirtualEiwa/apps/core/templates/requests/group_requests.html`
2. `AgendaVirtualEiwa/static/css/requests.css`

## Notas Técnicas

- La sección de información solo aparece cuando `proposed_changes` está vacío
- Se usa el filtro `|default:"Sin descripción"` para manejar tareas sin descripción
- Los estilos son consistentes con el resto de la plataforma
- El diseño es responsive y funciona en todos los dispositivos
