# Guía de Prueba - Indicador de Documentos (ACTUALIZADO)

## 🎯 Objetivo
Verificar que el indicador de solicitud aparezca solo cuando se adjuntan archivos, tanto en creación como en edición de tareas.

## 📋 Configuración Necesaria

### Permisos del Grupo
- **Crear tareas:** "Todos pueden crear"
- **Editar tareas:** "Todos pueden editar"
- **Subir documentos:** "Con aprobación del líder"

## ✅ Casos de Prueba - CREACIÓN

### Caso 1: Crear tarea SIN archivos
**Pasos:**
1. Ir a un grupo
2. Clic en "Nueva Tarea"
3. Completar formulario (materia, fechas, descripción)
4. NO adjuntar ningún archivo
5. Verificar que NO aparezca ningún aviso de solicitud
6. Clic en "Crear Tarea"

**Resultado esperado:**
- ✅ La tarea se crea directamente
- ✅ NO pasa por solicitud
- ✅ Aparece inmediatamente en la lista de tareas

---

### Caso 2: Crear tarea CON archivos
**Pasos:**
1. Ir a un grupo
2. Clic en "Nueva Tarea"
3. Completar formulario (materia, fechas, descripción)
4. Adjuntar uno o más archivos
5. **Verificar que aparezca el aviso azul:**
   ```
   📋 Solicitud de tarea con documentos
   Al adjuntar archivos, tu tarea será enviada como solicitud 
   para aprobación del líder del grupo.
   ```
6. Clic en "Enviar Solicitud"

**Resultado esperado:**
- ✅ Aparece el aviso azul al adjuntar archivos
- ✅ El botón cambia a "Enviar Solicitud"
- ✅ Se crea una TaskRequest (no una Task)
- ✅ El líder debe aprobarla

---

### Caso 3: Adjuntar y luego eliminar archivos (creación)
**Pasos:**
1. Ir a un grupo
2. Clic en "Nueva Tarea"
3. Completar formulario
4. Adjuntar un archivo → **Aparece el aviso azul**
5. Eliminar el archivo (clic en la X)
6. Verificar que el aviso desaparezca

**Resultado esperado:**
- ✅ El aviso aparece al adjuntar
- ✅ El aviso desaparece al eliminar todos los archivos
- ✅ Si se envía sin archivos, se crea directamente

---

## ✅ Casos de Prueba - EDICIÓN

### Caso 4: Editar tarea SIN agregar archivos
**Pasos:**
1. Ir a una tarea existente
2. Clic en "Editar"
3. Modificar descripción o fechas
4. NO adjuntar archivos nuevos
5. Verificar que NO aparezca aviso de solicitud
6. Clic en "Guardar Cambios"

**Resultado esperado:**
- ✅ La tarea se edita directamente
- ✅ NO pasa por solicitud
- ✅ Los cambios se aplican inmediatamente

---

### Caso 5: Editar tarea CON archivos nuevos
**Pasos:**
1. Ir a una tarea existente
2. Clic en "Editar"
3. Modificar descripción o fechas
4. Adjuntar uno o más archivos nuevos
5. **Verificar que aparezca el aviso azul:**
   ```
   📋 Solicitud de edición con documentos
   Al adjuntar archivos, tus cambios serán enviados como solicitud 
   para aprobación del líder del grupo.
   ```
6. Clic en "Enviar Solicitud de Edición"

**Resultado esperado:**
- ✅ Aparece el aviso azul al adjuntar archivos
- ✅ El botón cambia a "Enviar Solicitud de Edición"
- ✅ Se crea una TaskEditRequest
- ✅ El líder debe aprobarla
- ✅ Al aprobar, los cambios Y los archivos se aplican

---

### Caso 6: Adjuntar y luego eliminar archivos (edición)
**Pasos:**
1. Ir a una tarea existente
2. Clic en "Editar"
3. Adjuntar un archivo → **Aparece el aviso azul**
4. Eliminar el archivo (clic en la X)
5. Verificar que el aviso desaparezca
6. Clic en "Guardar Cambios"

**Resultado esperado:**
- ✅ El aviso aparece al adjuntar
- ✅ El aviso desaparece al eliminar todos los archivos
- ✅ Si se envía sin archivos nuevos, se edita directamente

---

### Caso 7: Aprobar solicitud de edición con archivos
**Pasos:**
1. Usuario normal edita tarea y adjunta archivos
2. Se crea TaskEditRequest
3. Líder va a "Solicitudes"
4. Revisa la solicitud de edición
5. Ve los archivos adjuntos en la solicitud
6. Aprueba la solicitud

**Resultado esperado:**
- ✅ Los cambios de texto se aplican a la tarea
- ✅ Los archivos se vinculan a la tarea
- ✅ Los archivos quedan en estado "approved"
- ✅ Los archivos son visibles para todos los miembros

---

### Caso 8: Adjuntar múltiples archivos
**Pasos:**
1. Crear o editar tarea
2. Adjuntar 3 archivos
3. Verificar que el aviso aparezca
4. Eliminar 2 archivos
5. Verificar que el aviso siga visible (queda 1 archivo)
6. Eliminar el último archivo
7. Verificar que el aviso desaparezca

**Resultado esperado:**
- ✅ El aviso permanece mientras haya al menos 1 archivo
- ✅ El aviso desaparece solo cuando NO hay archivos

---

## 🎨 Verificación Visual

### Aviso en CREACIÓN:
```
┌─────────────────────────────────────────────────────┐
│ ℹ️  Solicitud de tarea con documentos               │
│                                                      │
│    Al adjuntar archivos, tu tarea será enviada     │
│    como solicitud para aprobación del líder del     │
│    grupo.                                           │
└─────────────────────────────────────────────────────┘
```

### Aviso en EDICIÓN:
```
┌─────────────────────────────────────────────────────┐
│ ℹ️  Solicitud de edición con documentos             │
│                                                      │
│    Al adjuntar archivos, tus cambios serán         │
│    enviados como solicitud para aprobación del      │
│    líder del grupo.                                 │
└─────────────────────────────────────────────────────┘
```

**Características visuales:**
- Fondo azul claro con gradiente
- Borde izquierdo azul más oscuro
- Icono de información (ℹ️)
- Texto en azul oscuro
- Animación suave al aparecer

### En modo oscuro:
- Fondo azul oscuro translúcido
- Texto en azul claro
- Mantiene la misma estructura

---

## 🐛 Problemas Comunes

### El aviso no aparece
**Verificar:**
- ¿El permiso de documentos es "Con aprobación"?
- ¿Adjuntaste archivos correctamente?
- ¿El JavaScript está cargando sin errores?

### El aviso no desaparece
**Verificar:**
- ¿Eliminaste TODOS los archivos?
- Refrescar la página si es necesario

### La tarea/edición va a solicitud sin archivos
**Verificar:**
- ¿El permiso de crear/editar tareas es "Todos pueden"?
- Si es "Con aprobación", es normal que vaya a solicitud

### Los archivos no se vinculan al aprobar
**Verificar:**
- ¿El líder aprobó la solicitud correctamente?
- ¿Los archivos están en la TaskEditRequest?
- Revisar logs del servidor

---

## 📊 Matriz de Comportamiento

### CREACIÓN:
| Permiso Crear | Permiso Docs | Archivos | Resultado |
|--------------|--------------|----------|-----------|
| Todos | Con aprobación | ❌ No | ✅ Crea directamente |
| Todos | Con aprobación | ✅ Sí | ⏳ Va a solicitud |
| Con aprobación | Cualquiera | ❌ No | ⏳ Va a solicitud |
| Con aprobación | Cualquiera | ✅ Sí | ⏳ Va a solicitud |
| Solo líder | Cualquiera | - | ❌ No puede crear |

### EDICIÓN:
| Permiso Editar | Permiso Docs | Archivos Nuevos | Resultado |
|---------------|--------------|-----------------|-----------|
| Todos | Con aprobación | ❌ No | ✅ Edita directamente |
| Todos | Con aprobación | ✅ Sí | ⏳ Va a solicitud |
| Con aprobación | Cualquiera | ❌ No | ⏳ Va a solicitud |
| Con aprobación | Cualquiera | ✅ Sí | ⏳ Va a solicitud |
| Solo líder | Cualquiera | - | ❌ No puede editar |

---

## 🎯 Checklist Final

### Creación:
- [ ] Crear tarea sin archivos → Se crea directamente
- [ ] Crear tarea con archivos → Va a solicitud
- [ ] Aviso aparece al adjuntar archivos
- [ ] Aviso desaparece al eliminar todos los archivos

### Edición:
- [ ] Editar tarea sin archivos → Se edita directamente
- [ ] Editar tarea con archivos → Va a solicitud
- [ ] Aviso aparece al adjuntar archivos
- [ ] Aviso desaparece al eliminar todos los archivos
- [ ] Al aprobar solicitud, archivos se vinculan a la tarea

### Visual:
- [ ] Funciona en modo claro
- [ ] Funciona en modo oscuro
- [ ] Animación es suave y no intrusiva
- [ ] Mensajes adaptados (crear vs editar)

---

## 💡 Notas Adicionales

- El aviso es **dinámico**: aparece/desaparece según los archivos adjuntos
- Funciona tanto en **creación** como en **edición** de tareas
- La lógica es **inteligente**: solo va a solicitud si realmente hay archivos
- El diseño es **consistente** con el resto de la plataforma
- Los mensajes se **adaptan** al contexto (crear vs editar)
