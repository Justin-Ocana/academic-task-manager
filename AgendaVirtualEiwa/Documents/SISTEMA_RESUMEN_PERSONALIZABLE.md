# Sistema de Resumen de Actividades Personalizable

## 📋 Descripción General

Sistema que permite a cada usuario configurar cómo quiere ver su resumen de actividades en el dashboard. La plataforma se adapta a diferentes estilos de organización: estudiantes organizados, estudiantes que van día a día, y planificadores a largo plazo.

## ✨ Características Principales

### 1. Configuración Personalizable por Métrica

Cada bloque del dashboard se configura independientemente:

#### **Tareas Pendientes**
- **Hoy**: Solo tareas pendientes para hoy
- **Esta semana**: Tareas pendientes de la semana actual
- **Este mes**: Tareas pendientes del mes actual
- **Todas**: Todas las tareas pendientes activas

#### **Tareas Completadas**
- **Hoy**: Solo tareas completadas hoy
- **Esta semana**: Tareas completadas esta semana
- **Este mes**: Tareas completadas este mes
- **Siempre**: Todas las tareas completadas

#### **Tareas Vencidas**
- **Hoy**: Solo tareas vencidas hoy
- **Últimos 7 días**: Tareas vencidas en la última semana
- **Últimos 30 días**: Tareas vencidas en el último mes
- **Todas**: Todas las tareas vencidas

### 2. Perfiles de Usuario Predefinidos

El sistema incluye ejemplos de configuración para diferentes tipos de usuarios:

#### 📚 **Estudiante Organizado**
```
Pendientes: Semana
Completadas: Semana
Vencidas: 7 días
```
**Resultado**: Control equilibrado de actividades semanales

#### 🎯 **Enfoque Diario**
```
Pendientes: Hoy
Completadas: Hoy
Vencidas: Hoy
```
**Resultado**: Menos estrés, concentración en el día actual

#### 📅 **Planificador**
```
Pendientes: Mes
Completadas: Mes
Vencidas: 30 días
```
**Resultado**: Visión completa a largo plazo

## 🎨 Interfaz de Usuario

### Ubicación
**Configuración → Perfil → Pestaña "Preferencias"**

### Diseño
- Sección dedicada "Resumen de Actividades"
- Cada métrica con su propio grupo visual
- Opciones de radio buttons estilizados
- Tarjetas de ejemplo con casos de uso reales
- Diseño responsive y accesible

### Elementos Visuales
- Iconos descriptivos para cada métrica
- Gradientes sutiles para diferenciar secciones
- Animaciones suaves en hover
- Feedback visual al seleccionar opciones
- Modo oscuro completamente soportado

## 🔧 Implementación Técnica

### Modelo de Datos

**Campos agregados al modelo `User`:**

```python
pending_range = models.CharField(
    max_length=10,
    choices=[
        ('today', 'Hoy'),
        ('week', 'Esta semana'),
        ('month', 'Este mes'),
        ('all', 'Todas'),
    ],
    default='week'
)

completed_range = models.CharField(
    max_length=10,
    choices=[
        ('today', 'Hoy'),
        ('week', 'Esta semana'),
        ('month', 'Este mes'),
        ('all', 'Todas'),
    ],
    default='week'
)

overdue_range = models.CharField(
    max_length=10,
    choices=[
        ('today', 'Hoy'),
        ('7days', 'Últimos 7 días'),
        ('30days', 'Últimos 30 días'),
        ('all', 'Todas'),
    ],
    default='7days'
)
```

### Vista del Dashboard

La vista `dashboard()` en `apps/core/views.py` ahora:

1. Lee las preferencias del usuario
2. Calcula rangos de fechas según la configuración
3. Aplica filtros dinámicos a cada consulta
4. Retorna contadores personalizados

**Función auxiliar para calcular rangos:**

```python
def get_date_range(range_type):
    if range_type == 'today':
        return today, today
    elif range_type == 'week':
        week_start = today - timedelta(days=today.weekday())
        week_end = week_start + timedelta(days=6)
        return week_start, week_end
    elif range_type == 'month':
        month_start = today.replace(day=1)
        # Calcular último día del mes
        return month_start, month_end
    return None, None  # 'all'
```

### Vista de Configuración

**Endpoint**: `POST /settings/preferences/update/`

**Validación**:
- Verifica que los valores estén en las opciones válidas
- Guarda solo si pasan la validación
- Muestra mensaje de éxito/error

### Estilos CSS

**Archivo**: `static/css/profile-settings.css`

**Componentes principales**:
- `.summary-preference-group`: Contenedor de cada métrica
- `.summary-options`: Grid de opciones de radio
- `.summary-option`: Botón de radio estilizado
- `.example-cards`: Tarjetas de ejemplos de uso
- Soporte completo para modo oscuro

## 📊 Ventajas del Sistema

### Para el Usuario
1. **Reduce ansiedad**: No abruma con información innecesaria
2. **Personalización**: Se adapta a diferentes hábitos de estudio
3. **Flexibilidad**: Puede cambiar la configuración en cualquier momento
4. **Claridad**: Ve solo lo que necesita ver

### Para el Proyecto
1. **Diferenciación**: Característica única que otras apps escolares no tienen
2. **UX mejorada**: Experiencia más personalizada
3. **Retención**: Los usuarios sienten la plataforma como "propia"
4. **Escalabilidad**: Fácil agregar más opciones en el futuro

## 🚀 Uso

### Para Configurar

1. Ir a **Configuración** (icono de engranaje en el menú)
2. Seleccionar pestaña **"Preferencias"**
3. Encontrar sección **"Resumen de Actividades"**
4. Seleccionar las opciones deseadas para cada métrica
5. Hacer clic en **"Guardar Configuración"**
6. Volver al dashboard para ver los cambios

### Valores por Defecto

Si el usuario no configura nada, se usan estos valores:
- **Pendientes**: Semana
- **Completadas**: Semana
- **Vencidas**: Últimos 7 días

Estos valores representan un balance entre control y no abrumar al usuario.

## 🔄 Comportamiento del Dashboard

Cuando el usuario entra al dashboard:

1. El sistema carga su configuración personal
2. Aplica los filtros correspondientes a cada contador
3. Muestra los números personalizados
4. El mismo backend, diferente experiencia para cada usuario

## 📱 Responsive Design

El sistema es completamente responsive:

- **Desktop**: Grid de 3-4 columnas para opciones
- **Tablet**: Grid de 2 columnas
- **Mobile**: Columna única, opciones apiladas
- Tarjetas de ejemplo se adaptan al ancho disponible

## 🌙 Modo Oscuro

Soporte completo para modo oscuro:
- Colores adaptados para cada tema
- Contraste adecuado en todas las opciones
- Gradientes ajustados para mejor visibilidad
- Iconos y textos legibles en ambos modos

## 🔮 Futuras Mejoras

Posibles extensiones del sistema:

1. **Más métricas configurables**:
   - Rango de "Próximas tareas"
   - Filtro por prioridad
   - Filtro por materia

2. **Presets guardados**:
   - Guardar configuraciones favoritas
   - Cambiar rápido entre perfiles

3. **Configuración por grupo**:
   - Diferentes configuraciones para diferentes grupos
   - Vista unificada o separada

4. **Estadísticas avanzadas**:
   - Gráficos de productividad
   - Tendencias semanales/mensuales
   - Comparativas con periodos anteriores

## 📝 Notas de Implementación

### Migración de Base de Datos

Se agregaron 3 campos nuevos a la tabla `accounts_user`:
- `pending_range` (VARCHAR 10, default 'week')
- `completed_range` (VARCHAR 10, default 'week')
- `overdue_range` (VARCHAR 10, default '7days')

### Compatibilidad

- Compatible con usuarios existentes (valores por defecto)
- No requiere acción del usuario para funcionar
- Retrocompatible con versiones anteriores

### Performance

- Las consultas usan índices existentes
- Filtros aplicados a nivel de base de datos
- Sin impacto significativo en rendimiento
- Caché de preferencias en sesión (futuro)

## 🎯 Conclusión

Este sistema transforma el dashboard de una vista estática a una experiencia personalizada que se adapta a cada usuario. Es una característica diferenciadora que mejora significativamente la UX y hace que los usuarios sientan la plataforma como propia.

**Estado**: ✅ Implementado y funcional
**Versión**: 1.0
**Fecha**: Febrero 2026
