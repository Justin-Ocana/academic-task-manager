# Sistema de Estados de Tareas - Agenda Virtual EIWA

## Estados Oficiales

Una tarea puede estar en uno de estos estados:

### 1. Pendiente (`pending`)
- **Cuándo:** Fecha de entrega ≥ hoy
- **Características:**
  - Aparece en dashboard y filtros de "Activas"
  - Puede ser completada
  - Genera notificaciones
  - Se incluye en métricas

### 2. Vencida Reciente (`overdue_recent`)
- **Cuándo:** Fecha de entrega < hoy Y ≤ 30 días vencida
- **Características:**
  - Aparece en sección "Vencidas"
  - Puede ser completada
  - Genera notificaciones de vencimiento
  - Se incluye en métricas
  - Indicador visual de vencimiento

### 3. Completada (`completed`)
- **Cuándo:** Usuario marca como completada
- **Características:**
  - Aparece en sección "Completadas"
  - No genera notificaciones
  - Se incluye en métricas de rendimiento
  - Registro de fecha y usuario

### 4. Archivada (`archived`)
- **Cuándo:** Fecha de entrega < hoy Y > 30 días vencida
- **Características:**
  - Solo visible en filtro "Archivadas"
  - NO puede ser completada
  - NO genera notificaciones
  - NO se incluye en métricas activas
  - Solo lectura (registro histórico)

---

## Flujo Automático

### Creación de Tarea
```
Estado inicial: Pendiente
```

### Transiciones Automáticas

```
Pendiente → Vencida Reciente
  Condición: Pasa la fecha de entrega
  Tiempo: Día siguiente al vencimiento

Vencida Reciente → Archivada
  Condición: Más de 30 días vencida
  Tiempo: Día 31 después del vencimiento
  Acción: Se bloquea completado
```

### Transiciones Manuales

```
Pendiente → Completada
  Acción: Usuario marca como completada
  
Vencida Reciente → Completada
  Acción: Usuario marca como completada
  
Archivada → (bloqueada)
  Acción: No se puede completar
  Mensaje: "Esta tarea fue archivada por antigüedad"
```

---

## Comando de Mantenimiento

### Actualizar Estados Automáticamente

```bash
python manage.py update_task_statuses
```

**Qué hace:**
- Revisa todas las tareas activas
- Marca como "Vencida Reciente" las que correspondan
- Archiva automáticamente las que tengan > 30 días vencidas
- Registra cambios en el historial

**Cuándo ejecutar:**
- Diariamente (recomendado: cron job o tarea programada)
- Después de migraciones
- Manualmente cuando sea necesario

### Configurar Tarea Programada (Render/Producción)

Agregar a `render.yaml`:
```yaml
- type: cron
  name: update-task-statuses
  schedule: "0 2 * * *"  # Diariamente a las 2 AM
  command: python manage.py update_task_statuses
```

---

## Visibilidad por Sección

### Dashboard
- **Pendientes:** Solo `pending`
- **Completadas:** Solo `completed`
- **Vencidas:** Solo `overdue_recent`
- **Archivadas:** No se muestran

### Sección Tareas
Filtros disponibles:
- **Activas:** `pending` + `overdue_recent`
- **Completadas:** `completed`
- **Archivadas:** `archived`
- **Todas:** Todos los estados

### Calendario
- **Pendiente:** Color normal
- **Completada:** Check verde / color suave
- **Archivada:** Color tenue + badge "Archivada"
- Las archivadas son solo lectura

---

## Métricas y Contadores

```python
# Tareas activas (para métricas)
active_tasks = Task.objects.filter(status__in=['pending', 'overdue_recent'])

# Tareas completadas
completed_tasks = Task.objects.filter(status='completed')

# Tareas vencidas (solo recientes)
overdue_tasks = Task.objects.filter(status='overdue_recent')

# Archivadas (excluidas de métricas)
archived_tasks = Task.objects.filter(status='archived')
```

---

## Notificaciones

### Se envían para:
- ✅ Tareas pendientes (recordatorios)
- ✅ Tareas vencidas recientes (alertas)

### NO se envían para:
- ❌ Tareas archivadas
- ❌ Tareas completadas

---

## Registro e Historial

Todas las transiciones se guardan en `TaskHistory`:
- Cambio de estado
- Usuario responsable (si aplica)
- Fecha del cambio
- Razón (automática o manual)

Esto permite:
- Auditoría completa
- Análisis de patrones
- Transparencia en grupos
- Reversión si es necesario

---

## Propiedades del Modelo

### `task.get_computed_status()`
Calcula el estado que debería tener según las reglas

### `task.update_status()`
Actualiza el estado y registra el cambio

### `task.can_be_completed`
Verifica si la tarea puede ser completada (no archivada)

### `task.days_overdue`
Calcula cuántos días lleva vencida

---

## Frase de Diseño

> "El sistema prioriza tareas relevantes y archiva automáticamente las antiguas para mantener una organización clara sin perder el historial."

---

## Implementación Técnica

### Modelo actualizado
- ✅ Nuevos estados agregados
- ✅ Campo `archived_at` para tracking
- ✅ Métodos de cálculo de estado
- ✅ Validación de completado

### Comando de gestión
- ✅ `update_task_statuses` creado
- ✅ Actualización automática de estados
- ✅ Logging de cambios

### Vistas actualizadas
- ✅ Validación en `toggle_task_status`
- ✅ Mensaje de error para archivadas
- ✅ Actualización automática de estado

### Migraciones
- ✅ Migración aplicada
- ✅ Base de datos actualizada

---

## Próximos Pasos

1. **Actualizar filtros en vistas** para mostrar correctamente cada estado
2. **Agregar indicadores visuales** en templates (badges, colores)
3. **Configurar tarea programada** en producción
4. **Actualizar dashboard** para mostrar contadores correctos
5. **Agregar tests** para validar transiciones de estado
