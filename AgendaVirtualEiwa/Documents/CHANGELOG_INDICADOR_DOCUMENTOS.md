# Changelog - Indicador de Solicitud por Documentos (ACTUALIZADO)

## Fecha: 6 de febrero de 2026

## Cambios Implementados

### 1. Lógica Inteligente de Aprobación (Creación Y Edición)

**Problema anterior:**
- Al crear: Cuando un usuario tenía "todos pueden crear" + "documentos con aprobación", TODAS las tareas iban a solicitud, incluso sin archivos
- Al editar: Los archivos se agregaban en estado "pending" pero la tarea no se actualizaba hasta aprobación manual, causando confusión

**Solución implementada:**

#### En Creación de Tareas:
- La tarea solo va a solicitud si:
  - El usuario adjunta archivos Y el permiso de documentos es "con aprobación"
  - O si el permiso de crear tareas es "con aprobación" (independiente de archivos)
- Si NO hay archivos adjuntos y el permiso de crear es "todos", la tarea se crea directamente

#### En Edición de Tareas:
- La edición solo va a solicitud si:
  - El usuario adjunta archivos nuevos Y el permiso de documentos es "con aprobación"
  - O si el permiso de editar tareas es "con aprobación" (independiente de archivos)
- Si NO hay archivos nuevos y el permiso de editar es "todos", la tarea se edita directamente

**Código modificado:**
```python
# En views.py - create_task
has_attachments = can_upload_documents and 'attachments' in request.FILES and len(request.FILES.getlist('attachments')) > 0
force_approval_by_documents = has_attachments and documents_need_approval
requires_task_approval = needs_approval or force_approval_by_documents

# En views.py - edit_task
has_new_attachments = can_upload_documents and 'attachments' in request.FILES and len(request.FILES.getlist('attachments')) > 0
force_approval_by_documents = has_new_attachments and documents_need_approval
requires_edit_approval = needs_approval or force_approval_by_documents
```

### 2. Indicador Visual Dinámico (Creación Y Edición)

**Implementación:**
- Se agregó un aviso que aparece SOLO cuando el usuario adjunta archivos
- El aviso se muestra/oculta dinámicamente según si hay archivos en el input
- Usa animación suave (slideDown) para mejor UX
- **AHORA FUNCIONA TANTO EN CREACIÓN COMO EN EDICIÓN**

**Características:**
- Aparece en creación Y edición de tareas
- Solo se muestra si el permiso de documentos es "con aprobación"
- Desaparece automáticamente si el usuario elimina todos los archivos
- Diseño consistente con el resto de la plataforma
- Mensaje adaptado según el contexto (crear vs editar)

**Mensajes del indicador:**

En creación:
```
📋 Solicitud de tarea con documentos
Al adjuntar archivos, tu tarea será enviada como solicitud 
para aprobación del líder del grupo.
```

En edición:
```
📋 Solicitud de edición con documentos
Al adjuntar archivos, tus cambios serán enviados como solicitud 
para aprobación del líder del grupo.
```

### 3. Estilos CSS Agregados

**Nuevos estilos en tasks.css:**
- `.approval-notice` - Contenedor del aviso con gradiente azul
- Animación `@keyframes slideDown` para transición suave
- Soporte completo para modo oscuro
- También se agregó `.moderation-warning` para consistencia

**Características visuales:**
- Borde izquierdo destacado en azul (#2196f3)
- Gradiente de fondo suave
- Icono de información
- Responsive y accesible

## Archivos Modificados

1. **AgendaVirtualEiwa/apps/tasks/views.py**
   - Modificada lógica de `create_task` para verificar archivos adjuntos
   - Modificada lógica de `edit_task` para verificar archivos nuevos
   - Ambas funciones ahora solo van a solicitud si realmente hay archivos

2. **AgendaVirtualEiwa/apps/tasks/templates/tasks/task_form.html**
   - Reemplazado el aviso estático por uno dinámico
   - Agregada lógica JavaScript para mostrar/ocultar el aviso
   - Funciona tanto en creación como en edición
   - Mensajes adaptados según el contexto

3. **AgendaVirtualEiwa/static/css/tasks.css**
   - Agregados estilos para `.approval-notice`
   - Agregados estilos para `.moderation-warning`
   - Agregada animación `slideDown`
   - Soporte para modo oscuro

## Flujo de Usuario

### Escenario 1: Crear tarea con permiso "todos pueden crear" + documentos con aprobación

**Sin archivos adjuntos:**
1. Usuario completa el formulario
2. NO ve ningún aviso de solicitud
3. Hace clic en "Crear Tarea"
4. ✅ La tarea se crea directamente

**Con archivos adjuntos:**
1. Usuario completa el formulario
2. Adjunta uno o más archivos
3. 📋 Aparece el aviso: "Solicitud de tarea con documentos"
4. Hace clic en "Enviar Solicitud"
5. ⏳ Se crea una TaskRequest que el líder debe aprobar

### Escenario 2: Editar tarea con permiso "todos pueden editar" + documentos con aprobación

**Sin archivos nuevos:**
1. Usuario edita campos de la tarea
2. NO adjunta archivos nuevos
3. NO ve aviso de solicitud
4. Hace clic en "Guardar Cambios"
5. ✅ La tarea se edita directamente

**Con archivos nuevos:**
1. Usuario edita campos de la tarea
2. Adjunta uno o más archivos nuevos
3. 📋 Aparece el aviso: "Solicitud de edición con documentos"
4. Hace clic en "Enviar Solicitud de Edición"
5. ⏳ Se crea una TaskEditRequest que el líder debe aprobar
6. Al aprobar, los cambios Y los archivos se aplican a la tarea

### Escenario 3: Usuario con permiso "crear/editar con aprobación"

**Con o sin archivos:**
1. Usuario ve el aviso de solicitud desde el inicio
2. Completa el formulario
3. Hace clic en "Enviar Solicitud"
4. ⏳ Se crea una Request (siempre requiere aprobación)

## Beneficios

1. **Claridad:** El usuario sabe exactamente cuándo su acción será una solicitud
2. **Flexibilidad:** Permite crear/editar sin aprobación cuando no hay documentos
3. **UX mejorada:** Feedback visual inmediato al adjuntar archivos
4. **Consistencia:** Comportamiento lógico y predecible en creación Y edición
5. **Menos confusión:** Los archivos no quedan en estado "pending" sin contexto

## Pruebas Recomendadas

### Creación:
1. ✅ Crear tarea sin archivos (debe crearse directamente)
2. ✅ Crear tarea con archivos (debe ir a solicitud)
3. ✅ Adjuntar archivos y luego eliminarlos (aviso debe desaparecer)

### Edición:
4. ✅ Editar tarea sin agregar archivos (debe editarse directamente)
5. ✅ Editar tarea agregando archivos (debe ir a solicitud)
6. ✅ Adjuntar archivos y luego eliminarlos (aviso debe desaparecer)
7. ✅ Aprobar solicitud de edición con archivos (archivos deben vincularse a la tarea)

### Visual:
8. ✅ Verificar en modo oscuro
9. ✅ Verificar animación suave
10. ✅ Verificar mensajes adaptados (crear vs editar)

## Notas Técnicas

- El aviso usa `display: none` inicialmente y se muestra con JavaScript
- La función `updateFileList()` controla la visibilidad del aviso
- Se usa la variable de template `{% if documents_need_approval %}` para mostrar en ambos contextos
- La animación CSS es suave (0.3s) para no ser intrusiva
- Los mensajes se adaptan automáticamente según si es creación o edición con `{% if task %}`
