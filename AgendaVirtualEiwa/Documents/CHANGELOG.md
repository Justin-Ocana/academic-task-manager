# Changelog - Agenda Virtual Eiwa

Todos los cambios notables de este proyecto serán documentados en este archivo.

---

## [v1.0.2 "Refinamiento"] - 1 de Febrero, 2026

> Actualización de mantenimiento enfocada en corrección de bugs, optimizaciones y mejoras de UX

### 🎨 Nuevas Funcionalidades

#### Función de Eliminar Cuenta
- **Sistema completo de eliminación de cuenta** con nuevo diseño personalizado
- Modal de advertencia elegante con diseño de Agenda Virtual (sin prompt de navegador)
- Icono de advertencia con animación pulse
- Lista detallada de consecuencias de la eliminación:
  - Todos los datos personales
  - Todas las tareas creadas
  - Todos los grupos donde eres líder
  - Todo el historial de actividad
- Input de confirmación que requiere escribir el email exacto
- Botón deshabilitado hasta que el email coincida
- Validación robusta en frontend y backend
- Eliminación en cascada automática de todos los datos del usuario
- Logout automático después de eliminar
- Animación shake si el email no coincide
- Respuesta JSON para mejor UX
- **Nota:** No envía confirmación por email (funcionalidad pendiente)

#### Sistema de Validación de Nombres Mejorado
- **Validadores personalizados** para nombres, apellidos y materias
- Validación en 3 capas: Frontend (HTML5), Formularios (Django Forms), Modelos (Django Models)
- Límites estrictos y realistas:
  - Nombres y apellidos: 2-20 caracteres
  - Materias: 2-40 caracteres
- Reglas anti-troll:
  - Solo letras (con acentos y ñ permitidos)
  - Máximo 2 letras iguales seguidas en nombres
  - Máximo 3 caracteres iguales seguidos en materias
  - Sin números ni símbolos en nombres
- Archivo `validators.py` con funciones `validate_name` y `validate_subject_name`

#### Modo Oscuro
- **Implementación completa del modo oscuro** en toda la aplicación
- Sistema de carga que reduce el flash blanco al cargar páginas (parcialmente eliminado)
- Script inline en `<head>` que aplica el tema antes de renderizar contenido
- Estilos críticos inline para evitar parpadeos
- Clase `theme-ready` para habilitar transiciones solo después de la carga
- Pseudo-elemento `::before` con fondo oscuro fijo como respaldo
- Modal de advertencia al activar modo oscuro (experimental)
- **Nota:** Funcional en toda la app, pero falta ajustar algunos colores para mejor coincidencia visual

### 🎨 Optimizaciones de Modo Oscuro

#### Componentes Optimizados
- ✅ Dashboard principal
- ✅ Sidebar y navegación
- ✅ Header y notificaciones
- ✅ Menú de perfil (dropdown)
- ✅ Calendario (vista mensual y semanal)
- ✅ Grupos (lista, detalle, configuración)
- ✅ Tareas (lista, detalle, formularios)
- ✅ Materias
- ✅ Solicitudes (requests)
- ✅ Tracking/Historial
- ✅ Configuración de perfil
- ✅ Configuración de preferencias
- ✅ Changelog/Actualizaciones
- ✅ Modales de confirmación
- ✅ Alertas y warnings
- ✅ Dropdown menus
- ✅ Formularios
- ✅ Botones y controles
- ✅ Empty states
- ✅ Footer

### 🔧 Mejoras Técnicas

#### Optimización de Z-Index
- Dropdown de acciones de miembros: z-index: 99999
- Member-card con dropdown activo: z-index: 100000
- Uso de `:has()` selector para elevar tarjetas con dropdown abierto
- Contexto de apilamiento correcto con `position: relative`

#### Prevención de Flash Blanco
- Script inline que se ejecuta antes de cargar CSS
- Aplicación de colores críticos con `style.setProperty()`
- Estilos inline con `!important` para forzar colores
- Eliminación de transiciones durante la carga inicial
- Sistema de clase `theme-ready` para habilitar animaciones después

#### Validación de Formularios
- Pattern HTML5 para validación en frontend
- Atributo `maxlength` en todos los inputs
- Validadores Django personalizados
- Mensajes de error descriptivos
- Help text informativo en formularios

#### Protección de Formularios
- Sistema mejorado de protección contra múltiples envíos
- Restauración correcta de estado al cancelar
- Preservación de HTML completo (incluyendo SVG)
- Manejo de eventos con `stopImmediatePropagation()`

### 🐛 Correcciones

#### Modo Oscuro
- Flash blanco parcialmente reducido al cargar páginas (aún presente en algunos casos)
- Corregidos bordes blancos en preference items
- Corregidos colores de texto en diversos componentes
- Corregidas sombras y bordes en modo oscuro

#### Dropdown y Menús
- Corregido z-index de dropdown de acciones de miembros
- Dropdown ahora aparece siempre por encima de otros elementos
- Corregido posicionamiento de menús desplegables

#### Botones de Eliminación
- Corregido problema de botones que quedaban en estado "enviando"
- Corregido problema de iconos que desaparecían al cancelar
- Corregida barra de progreso que aparecía incorrectamente
- Restauración completa de estado al cancelar confirmación

#### Validación de Nombres
- Implementados límites realistas (20 caracteres para nombres)
- Prevención de nombres trolls (aaaaaaaaaa, XxDarkLordxX, etc.)
- Validación en frontend y backend
- Mensajes de error claros y descriptivos

### 🔒 Seguridad

- Validación en 3 capas (Frontend, Forms, Models)
- Prevención de inyección de caracteres especiales
- Límites estrictos para prevenir ataques de longitud
- Validación de patrones con regex seguras
- Sanitización de entrada en validadores personalizados
- Confirmación múltiple para eliminación de cuenta
- Verificación de email exacta antes de eliminar

### 📱 Responsive

- Modo oscuro funciona en todos los tamaños de pantalla
- Validaciones funcionan en móviles
- Dropdowns adaptados para móviles
- Modales responsive en modo oscuro
- Modal de eliminación de cuenta adaptado a móviles

### 🚀 Mejoras de Rendimiento

- Carga instantánea del tema sin flash
- Transiciones deshabilitadas durante carga inicial
- Z-index optimizado para mejor rendimiento de composición
- Validación en frontend reduce llamadas al servidor
- Pattern HTML5 previene envíos inválidos

---

## [v1.0.1 "Moderación Inteligente"] - 10 de Diciembre, 2025

> Actualización mayor con sistema de moderación de contenido y mejoras visuales

### ✨ Nuevas Funcionalidades
- Sistema de notificaciones en tiempo real
- Calendario con vista mensual y semanal
- Gestión de grupos de estudio
- Sistema de solicitudes y aprobaciones
- Tracking de cambios y reversión de acciones

### 🎨 Mejoras de Diseño
- Interfaz moderna con gradientes
- Animaciones suaves
- Diseño responsive completo
- Iconos SVG personalizados

### 🔧 Mejoras Técnicas
- Optimización de consultas a base de datos
- Sistema de caché implementado
- Mejoras en seguridad
- Validación de formularios mejorada

---

## [v1.0.0 "Génesis"] - Lanzamiento Inicial

> Primera versión pública de Agenda Virtual Eiwa

### 🎉 Características Principales
- Sistema de autenticación de usuarios
- Gestión de tareas personales
- Calendario académico
- Gestión de materias
- Dashboard personalizado
- Sistema de grupos colaborativos
- Notificaciones básicas

### 🎨 Diseño
- Paleta de colores EIWA (azul y naranja)
- Tipografía Bebas Neue y Montserrat
- Diseño responsive
- Interfaz intuitiva

### 🔒 Seguridad
- Autenticación segura
- Protección CSRF
- Validación de datos
- Permisos por usuario

---

**Desarrollado con ❤️ por Justin Ocaña**  
**Proyecto académico estudiantil - EIWA**
