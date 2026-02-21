# Sistema Multigrupo - Documentación

## Resumen
Sistema MVP que permite a los usuarios elegir cómo visualizar sus tareas, calendario y resumen cuando pertenecen a múltiples grupos.

## Características Implementadas

### 1. Modelo de Usuario (accounts/models.py)
Se agregaron dos nuevos campos al modelo `User`:

- **multigroup_mode**: CharField con opciones:
  - `separated` (por defecto): Mantener grupos separados
  - `unified`: Unificar todos los grupos

- **last_active_group**: ForeignKey a Group (nullable)
  - Guarda el último grupo activo cuando está en modo separado
  - Se actualiza automáticamente al visitar tareas de un grupo

### 2. Configuración de Preferencias (profile_views.py)
- Nueva sección en configuración de perfil para elegir modo multigrupo
- Formulario actualizado para guardar la preferencia del usuario
- Validación de valores permitidos

### 3. Dashboard (core/views.py)

#### Modo Unificado
- Muestra tareas de **todos los grupos**
- Contadores suman todas las tareas
- Estadísticas por grupo muestran todos los grupos
- URLs redirigen a vista unificada de tareas

#### Modo Separado
- Muestra tareas del **grupo activo** únicamente
- Si no hay grupo activo y tiene múltiples grupos, no muestra datos
- Si solo tiene un grupo, lo usa automáticamente
- URLs redirigen al grupo activo específico

### 4. Tareas (tasks/views.py)

#### Vista `task_list()`
- Detecta el modo multigrupo del usuario
- **Modo Unificado**: Redirige a `unified_tasks_view()`
- **Modo Separado**: Comportamiento original (lista de grupos o redirige si solo tiene uno)

#### Nueva Vista `unified_tasks_view()`
- Muestra todas las tareas de todos los grupos en una sola lista
- Cada tarea muestra badge con nombre del grupo
- **Filtros disponibles**:
  - Por grupo (nuevo)
  - Por estado (pendiente, completada, archivada)
  - Por materia
  - Por tiempo (hoy, mañana, esta semana, etc.)
- **Ordenamiento**:
  - Por fecha de entrega
  - Por fecha de creación
  - Por materia
  - Por grupo (nuevo)
- Template: `unified_tasks.html`

#### Vista `group_tasks()`
- Actualizada para guardar el último grupo activo
- Solo guarda si está en modo separado
- Actualización eficiente usando `update_fields`

### 5. Calendario (calendar_app/views.py)

#### Vista Principal (`calendar_view`)
- **Modo Separado**:
  - Si no hay grupo activo y tiene múltiples grupos: muestra modal de selección
  - Si solo tiene un grupo: lo usa automáticamente
  - Materias solo del grupo activo

- **Modo Unificado**:
  - Muestra todas las materias de todos los grupos
  - No requiere selección de grupo

#### API de Datos (`calendar_data`)
- Respeta el modo multigrupo del usuario
- En modo separado: filtra por `last_active_group`
- En modo unificado: muestra todos los grupos (con opción de filtrar)

#### Nueva Vista (`set_active_group`)
- Endpoint POST para cambiar el grupo activo
- Valida que el usuario pertenezca al grupo
- Retorna JSON con éxito/error

### 6. Template de Configuración (profile_settings.html)
Nueva sección "Visualización Multigrupo" con:
- Dos opciones visuales con radio buttons
- Iconos descriptivos para cada modo
- Lista de características de cada modo
- Mensaje informativo sobre el impacto
- Diseño responsive

### 7. Estilos CSS (profile-settings.css)
Nuevos estilos para:
- `.multigroup-options`: Contenedor de opciones
- `.multigroup-option`: Cada opción seleccionable
- `.option-content`: Layout de contenido
- `.option-icon`: Icono circular con gradiente
- `.option-text`: Texto descriptivo
- `.option-features`: Lista de características
- `.multigroup-info`: Mensaje informativo
- Responsive para móviles

### 8. URLs (calendar_app/urls.py)
Nueva ruta agregada:
```python
path('api/set-active-group/', views.set_active_group, name='set_active_group')
```

### 9. Migración (0007_user_multigroup_mode_user_last_active_group.py)
- Agrega campo `multigroup_mode` con valor por defecto `separated`
- Agrega campo `last_active_group` nullable con FK a Group
- Dependencias correctas con app groups

## Flujo de Usuario

### Configuración Inicial
1. Usuario va a Configuración → Preferencias
2. Ve la sección "Visualización Multigrupo"
3. Elige entre "Mantener grupos separados" o "Unificar todos los grupos"
4. Guarda la configuración

### Modo Separado
1. Usuario entra al dashboard → ve datos del grupo activo
2. Usuario entra a tareas → selecciona un grupo → se guarda como activo
3. Usuario entra al calendario:
   - Si no hay grupo activo: modal pide seleccionar
   - Si hay grupo activo: muestra ese calendario
4. Cambiar de grupo actualiza automáticamente el grupo activo

### Modo Unificado
1. Usuario entra al dashboard → ve datos de todos los grupos
2. Usuario entra a tareas → ve **vista unificada** con todas las tareas
   - Cada tarea muestra badge del grupo
   - Puede filtrar por grupo específico
   - Puede ordenar por grupo
3. Usuario entra al calendario → ve eventos de todos los grupos con colores por grupo
4. No necesita seleccionar grupo

## Reglas Importantes

### Valor por Defecto
- **SIEMPRE** `separated` para no romper el uso actual
- Usuarios existentes mantienen comportamiento separado

### Persistencia
- El sistema recuerda la elección del usuario
- No pregunta cada vez
- `last_active_group` se actualiza automáticamente

### Consistencia
- El modo elegido afecta: tareas, calendario y dashboard
- No hay mezcla de comportamientos
- URLs generadas respetan el modo activo

### Seguridad
- Validación de pertenencia a grupos
- No se puede establecer grupo activo si no eres miembro
- ForeignKey con `SET_NULL` para evitar errores si se elimina el grupo

## Casos Especiales

### Usuario con 1 Solo Grupo
- Modo separado: usa ese grupo automáticamente
- Modo unificado: funciona igual (solo hay uno)
- No necesita seleccionar

### Usuario sin Grupos
- Dashboard muestra mensaje de bienvenida
- No hay datos para mostrar
- Invita a unirse a un grupo

### Usuario sin Grupo Activo (Modo Separado)
- Dashboard no muestra datos hasta seleccionar
- Calendario muestra modal de selección
- Tareas redirige a lista de grupos

## Testing Recomendado

1. **Crear usuario con múltiples grupos**
2. **Probar modo separado**:
   - Verificar que solo muestra un grupo
   - Cambiar de grupo y verificar persistencia
   - Revisar calendario requiere selección
3. **Probar modo unificado**:
   - Verificar que muestra todos los grupos
   - Cada tarea muestra su grupo
   - Calendario muestra todos los eventos
4. **Cambiar entre modos**:
   - Verificar que el cambio es inmediato
   - Dashboard se actualiza correctamente
5. **Casos edge**:
   - Usuario con 1 grupo
   - Usuario sin grupos
   - Eliminar grupo activo

## Archivos Modificados

### Backend
- `apps/accounts/models.py` - Campos multigroup_mode y last_active_group
- `apps/core/views.py` - Dashboard con lógica multigrupo
- `apps/core/profile_views.py` - Guardar preferencia multigrupo
- `apps/tasks/views.py` - Guardar último grupo activo
- `apps/calendar_app/views.py` - Lógica multigrupo en calendario
- `apps/calendar_app/urls.py` - Nueva ruta set_active_group

### Frontend
- `apps/core/templates/settings/profile_settings.html` - Nueva sección UI
- `static/css/profile-settings.css` - Estilos para multigrupo

### Migraciones
- `apps/accounts/migrations/0007_user_multigroup_mode_user_last_active_group.py`

## Próximos Pasos (Opcional)

1. **JavaScript para calendario**: Modal de selección de grupo
2. **Indicador visual**: Mostrar grupo activo en navbar
3. **Selector rápido**: Dropdown para cambiar grupo sin ir a configuración
4. **Estadísticas**: Comparar rendimiento entre grupos en modo unificado
5. **Notificaciones**: Respetar modo multigrupo en notificaciones

## Notas Técnicas

- Uso de `update_fields` para optimizar guardado de `last_active_group`
- Queries optimizadas con `select_related` y `prefetch_related`
- Validación en backend y frontend
- Diseño mobile-first en CSS
- Accesibilidad con labels y ARIA
