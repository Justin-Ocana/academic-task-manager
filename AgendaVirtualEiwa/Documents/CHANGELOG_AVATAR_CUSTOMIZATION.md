# Sistema de Personalización de Avatar

## Fecha: 6 de Febrero de 2026

## Descripción
Se ha implementado un sistema completo de personalización de avatar para los usuarios de Agenda Virtual Eiwa, permitiendo elegir entre 16 diseños diferentes y personalizar tanto el color de fondo como el color del diseño SVG.

## Características Principales

### 1. **Modales Desplegables**
Los selectores de color ahora son modales colapsables que se pueden abrir/cerrar:
- **Color de Fondo**: Modal con 25 colores + personalizado
- **Color del Diseño**: Modal con 25 colores + personalizado
- Vista previa del color seleccionado en el botón del modal
- Animación suave al expandir/colapsar
- Solo un modal abierto a la vez para mejor UX

### 2. **25 Colores Predefinidos** (incluyendo blanco)
Paleta completa disponible para ambos selectores:
- ✅ Blanco (#FFFFFF) - Ahora disponible
- ✅ Rojos (3 tonos)
- ✅ Naranjas y Amarillos (5 tonos)
- ✅ Verdes (4 tonos)
- ✅ Azules y Cianes (4 tonos)
- ✅ Morados y Rosas (4 tonos)
- ✅ Grises y Neutros (4 tonos)

### 3. **Doble Personalización de Color**

#### Color de Fondo
- Cambia el color del círculo de fondo del avatar
- Gradiente automático aplicado
- Vista previa en tiempo real

#### Color del Diseño (SVG)
- Cambia el color del diseño/forma del avatar
- Permite combinaciones creativas
- Ejemplo: Fondo rojo con diseño blanco, o fondo blanco con diseño negro

### 4. **Triple Método de Personalización** (para cada color)

**Método 1: Selector Visual**
- Input nativo HTML5 type="color"
- Optimizado para móvil
- Interfaz del sistema operativo

**Método 2: RGB Manual**
- 3 inputs numéricos (R, G, B)
- Rango 0-255 con validación

**Método 3: HEX Editable**
- Input de texto para código hexadecimal
- Formato #RRGGBB
- Validación automática

### 5. **Sincronización Automática**
- Los 3 métodos están sincronizados en tiempo real
- Cambiar uno actualiza automáticamente los otros dos
- Vista previa se actualiza instantáneamente
- Funciona independientemente para fondo y diseño

## Archivos Creados/Modificados

### 1. Template HTML
**Archivo:** `AgendaVirtualEiwa/apps/core/templates/settings/avatar_settings.html`
- Estructura de modales desplegables
- Dos selectores de color independientes
- 16 avatares SVG con diseños variados
- Generación dinámica de colores vía JavaScript

### 2. Estilos CSS
**Archivo:** `AgendaVirtualEiwa/static/css/avatar-settings.css`
- Estilos para modales colapsables
- Animaciones de expansión/colapso
- Botones de toggle con preview
- Diseño responsive

### 3. JavaScript
**Archivo:** `AgendaVirtualEiwa/static/js/avatar-settings.js`
- Generación dinámica de selectores de color
- Manejo de modales desplegables
- Sincronización de colores (fondo y SVG)
- Actualización en tiempo real de vista previa
- Conversión RGB ↔ HEX para ambos colores

## Experiencia de Usuario

### Flujo de Trabajo
1. **Seleccionar Avatar**: Click en uno de los 16 diseños
2. **Personalizar Color de Fondo**:
   - Click en botón "Color de Fondo" para expandir
   - Elegir color predefinido o personalizado
   - Ver preview en tiempo real
3. **Personalizar Color del Diseño**:
   - Click en botón "Color del Diseño" para expandir
   - Elegir color predefinido o personalizado
   - Ver preview en tiempo real
4. **Vista Previa**: Avatar circular con diseño y colores elegidos
5. **Guardar**: Click en botón "En Desarrollo"

### Ventajas del Sistema de Modales

**Para el Usuario:**
- ✅ Interfaz más limpia y organizada
- ✅ Menos scroll necesario
- ✅ Enfoque en una opción a la vez
- ✅ Vista previa del color en el botón
- ✅ Fácil de entender y usar

**Para Móviles:**
- ✅ Menos contenido visible simultáneamente
- ✅ Mejor uso del espacio vertical
- ✅ Touch-friendly
- ✅ Animaciones suaves

## Combinaciones Populares Sugeridas

### Clásicas
- Fondo Rojo + Diseño Blanco
- Fondo Azul + Diseño Blanco
- Fondo Negro + Diseño Blanco

### Modernas
- Fondo Blanco + Diseño Negro
- Fondo Turquesa + Diseño Blanco
- Fondo Lavanda + Diseño Blanco

### Vibrantes
- Fondo Amarillo + Diseño Negro
- Fondo Magenta + Diseño Blanco
- Fondo Verde Lima + Diseño Negro

### Elegantes
- Fondo Azul Oscuro + Diseño Dorado
- Fondo Gris Oscuro + Diseño Blanco
- Fondo Negro + Diseño Dorado

## Estado Actual
- ✅ Interfaz completa y funcional
- ✅ Modales desplegables
- ✅ Vista previa en tiempo real
- ✅ Doble selector de color (fondo + diseño)
- ✅ 25 colores predefinidos (incluyendo blanco)
- ✅ Selector RGB personalizado
- ✅ Integración con página de perfil
- ⏳ Guardado en base de datos (pendiente)
- ⏳ Aplicación del avatar en toda la app (pendiente)

## Próximos Pasos Sugeridos
1. Agregar campos al modelo de Usuario:
   - `avatar_style` (CharField con choices)
   - `avatar_bg_color` (CharField para HEX)
   - `avatar_svg_color` (CharField para HEX)
2. Implementar la vista POST para guardar cambios
3. Crear template tag para renderizar el avatar del usuario
4. Aplicar el avatar personalizado en toda la aplicación
5. Agregar opción de resetear a avatar por defecto
6. Implementar sistema de favoritos/guardados

## Notas Técnicas
- Los colores se generan dinámicamente vía JavaScript
- Los modales usan CSS transitions para animaciones suaves
- El blanco tiene borde especial para visibilidad
- Los SVG usan `currentColor` para facilitar cambios
- Compatible con todos los navegadores modernos
- Sin dependencias externas

## Archivos Creados

### 1. Template HTML
**Archivo:** `AgendaVirtualEiwa/apps/core/templates/settings/avatar_settings.html`
- Página de personalización de avatar
- 16 avatares SVG con diseños variados y personajes:
  1. **Smile** - Cara sonriente clásica
  2. **Cat** - Gatito con orejas
  3. **Star Eyes** - Ojos de estrella
  4. **Robot** - Robot futurista
  5. **Heart** - Ojos de corazón
  6. **Glasses** - Con lentes
  7. **Music** - Musical con notas
  8. **Wink** - Guiño coqueto
  9. **Cool** - Con lentes de sol
  10. **Bear** - Osito tierno
  11. **Lightning** - Ojos de rayo
  12. **Flower** - Corona de flores
  13. **Alien** - Extraterrestre
  14. **Crown** - Con corona real
  15. **Ninja** - Ninja misterioso
  16. **Party** - Fiesta con confeti

### 2. Estilos CSS
**Archivo:** `AgendaVirtualEiwa/static/css/avatar-settings.css`
- Estilos consistentes con el diseño de la aplicación
- Selector de colores similar al de materias
- Animaciones y transiciones suaves
- Diseño responsive

### 3. JavaScript
**Archivo:** `AgendaVirtualEiwa/static/js/avatar-settings.js`
- Actualización en tiempo real de la vista previa
- Selector de color RGB personalizado
- Conversión automática RGB a HEX
- Animaciones interactivas
- Prevención de envío de formulario (modo desarrollo)

### 4. Vista Django
**Archivo:** `AgendaVirtualEiwa/apps/core/profile_views.py`
- Nueva función `avatar_settings()` para renderizar la página

### 5. URL
**Archivo:** `AgendaVirtualEiwa/AgendaVirtualEiwa/urls.py`
- Ruta: `/settings/avatar/`
- Nombre: `avatar_settings`

## Características Implementadas

### Selector de Formas
- 16 diseños SVG variados con personajes y expresiones
- Visualización en cuadrícula responsive
- Selección con radio buttons
- Animaciones al seleccionar y hover
- Indicador visual de selección
- Diseños circulares que se adaptan al formato de avatar

### Selector de Colores
- 24 colores predefinidos organizados por categorías:
  - **Rojos:** Rojo puro, Rojo Coral, Rosa Suave
  - **Naranjas y Amarillos:** Naranja Oscuro, Salmón, Dorado, Amarillo puro, Amarillo Dorado
  - **Verdes:** Verde Lima, Verde Limón, Verde Menta, Verde Agua
  - **Azules y Cianes:** Cian, Turquesa, Azul puro, Azul Cielo
  - **Morados y Rosas:** Magenta, Lavanda, Púrpura Medio, Melocotón
  - **Grises y Neutros:** Gris, Gris Oscuro, Azul Oscuro, Gris Azulado
- Opción de color personalizado con tres métodos:
  1. **Selector Visual** - Input nativo HTML5 tipo "color" (optimizado para móvil)
  2. **RGB Manual** - Inputs numéricos para R, G, B (0-255)
  3. **HEX Editable** - Input de texto para código hexadecimal
- Conversión automática entre RGB y HEX
- Sincronización en tiempo real entre los tres métodos
- Estilo idéntico al selector de colores de materias

### Vista Previa en Tiempo Real
- Avatar grande CIRCULAR (como se verá en el perfil)
- Actualización instantánea al cambiar opciones
- Animaciones suaves de transición
- Gradiente aplicado al color de fondo
- Información del usuario (nombre y email)
- Formato circular para coincidir con los avatares de perfil

### Integración con Perfil
**Archivo modificado:** `AgendaVirtualEiwa/apps/core/templates/settings/profile_settings.html`
- Avatar ahora es un botón clickeable
- Icono de edición aparece al hacer hover
- Botón "Cambiar Avatar" debajo de la información del usuario
- Enlace directo a la página de personalización

**Archivo modificado:** `AgendaVirtualEiwa/static/css/profile-settings.css`
- Estilos para el avatar como botón
- Animaciones de hover
- Icono de edición con transiciones

## Diseño y UX

### Consistencia Visual
- Mismo estilo que el selector de colores de materias
- Paleta de colores de Agenda Virtual Eiwa
- Tipografía Bebas Neue para títulos
- Tipografía Montserrat para texto

### Animaciones
- Transiciones suaves en todas las interacciones
- Efecto de bounce al cambiar avatar
- Gradiente animado en opción de color personalizado
- Shimmer effect en botón "En Desarrollo"

### Responsive
- Diseño adaptable a móviles
- Grid flexible para avatares y colores
- Botones de acción apilados en móvil

## Estado Actual
- ✅ Interfaz completa y funcional
- ✅ Vista previa en tiempo real
- ✅ Selector de colores RGB personalizado
- ✅ Integración con página de perfil
- ⏳ Guardado en base de datos (pendiente)
- ⏳ Aplicación del avatar en toda la app (pendiente)

## Botón "En Desarrollo"
El botón de guardar muestra "En Desarrollo" y no guarda los cambios actualmente. Esto es intencional para indicar que la funcionalidad de persistencia está pendiente de implementación.

## Próximos Pasos Sugeridos
1. Agregar campos al modelo de Usuario para guardar:
   - `avatar_style` (CharField con choices)
   - `avatar_color` (CharField para HEX)
2. Implementar la vista POST para guardar cambios
3. Crear template tag para renderizar el avatar del usuario
4. Aplicar el avatar personalizado en:
   - Dashboard
   - Perfil
   - Comentarios/Actividades
   - Navbar
5. Agregar opción de resetear a avatar por defecto

## Notas Técnicas
- Los SVG usan `viewBox` para ser escalables
- Los colores se aplican con `currentColor` para facilitar cambios
- El JavaScript es vanilla (sin dependencias)
- Compatible con todos los navegadores modernos
