# Advertencia Experimental - Subida de Documentos

## Fecha: 6 de febrero de 2026

## Implementación

Se agregó una advertencia visual que aparece cuando el usuario activa la función de subida de documentos en la creación o configuración de grupos.

## Ubicación

La advertencia aparece en:
1. **Creación de grupos** (`create_group.html`)
2. **Configuración de grupos** (`group_settings.html`)

## Comportamiento

### Cuándo aparece:
- ✅ Cuando el usuario marca el checkbox "Habilitar subida de documentos"
- ✅ Aparece con animación suave (slideDown)
- ✅ Se muestra debajo del checkbox y encima de los permisos

### Cuándo desaparece:
- ✅ Cuando el usuario desmarca el checkbox
- ✅ Desaparece suavemente

## Diseño Visual

```
┌─────────────────────────────────────────────────────┐
│ ⚠️  Función Experimental                            │
│                                                     │
│ La subida de documentos está en fase de prueba.    │
│ Puede presentar pequeños errores. Estamos          │
│ trabajando para mejorarla continuamente.           │
└─────────────────────────────────────────────────────┘
```

### Características:
- 🎨 Fondo amarillo con gradiente
- ⚠️ Icono de advertencia triangular
- 🔶 Borde izquierdo naranja destacado
- ✨ Animación de entrada suave
- 🌙 Soporte completo para modo oscuro

## Código HTML

```html
<div id="experimentalWarning" class="experimental-warning" style="display: none;">
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path>
    </svg>
    <div>
        <strong>⚠️ Función Experimental</strong>
        <p>La subida de documentos está en fase de prueba. Puede presentar pequeños errores. Estamos trabajando para mejorarla continuamente.</p>
    </div>
</div>
```

## Código JavaScript

```javascript
function toggleDocumentPermissions() {
    if (documentsCheckbox.checked) {
        permissionGroup.style.display = 'block';
        if (experimentalWarning) {
            experimentalWarning.style.display = 'flex';
        }
    } else {
        permissionGroup.style.display = 'none';
        if (experimentalWarning) {
            experimentalWarning.style.display = 'none';
        }
    }
}
```

## Estilos CSS

### Modo Claro:
- Fondo: Gradiente amarillo (#fff3cd → #ffeaa7)
- Borde: Amarillo (#ffc107) con borde izquierdo naranja (#ff9800)
- Texto: Naranja oscuro (#ef6c00)
- Título: Naranja más oscuro (#e65100)
- Icono: Naranja (#f57c00)

### Modo Oscuro:
- Fondo: Naranja translúcido (rgba(255, 152, 0, 0.15))
- Borde: Naranja translúcido (rgba(255, 183, 77, 0.3))
- Texto: Naranja claro (#ffe0b2)
- Título: Naranja pastel (#ffcc80)
- Icono: Naranja medio (#ffb74d)

## Animación

```css
@keyframes slideDown {
    from {
        opacity: 0;
        transform: translateY(-10px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}
```

Duración: 0.3 segundos
Efecto: ease

## Archivos Modificados

1. **AgendaVirtualEiwa/apps/groups/templates/groups/create_group.html**
   - Agregado div de advertencia experimental
   - Actualizado JavaScript para mostrar/ocultar advertencia
   - Agregados estilos CSS para la advertencia

2. **AgendaVirtualEiwa/apps/groups/templates/groups/group_settings.html**
   - Agregado div de advertencia experimental
   - Actualizado JavaScript para mostrar/ocultar advertencia
   - Agregados estilos CSS para la advertencia

## Mensaje de la Advertencia

**Título:** ⚠️ Función Experimental

**Contenido:** La subida de documentos está en fase de prueba. Puede presentar pequeños errores. Estamos trabajando para mejorarla continuamente.

## Propósito

1. **Transparencia:** Informar al usuario que la función está en desarrollo
2. **Expectativas:** Establecer que puede haber errores menores
3. **Confianza:** Mostrar que se está trabajando en mejoras
4. **UX:** Evitar frustraciones por bugs inesperados

## Beneficios

- ✅ Usuario informado antes de activar la función
- ✅ Reduce quejas por bugs menores
- ✅ Genera confianza al ser transparentes
- ✅ Permite recopilar feedback de usuarios conscientes
- ✅ Protege la reputación de la plataforma

## Pruebas Recomendadas

1. ✅ Activar checkbox → Advertencia aparece
2. ✅ Desactivar checkbox → Advertencia desaparece
3. ✅ Verificar animación suave
4. ✅ Verificar en modo oscuro
5. ✅ Verificar en móvil
6. ✅ Verificar en creación de grupo
7. ✅ Verificar en configuración de grupo

## Responsive

La advertencia es completamente responsive:
- Se adapta al ancho del contenedor
- El texto se ajusta automáticamente
- El icono mantiene su tamaño
- Funciona en todos los dispositivos

## Accesibilidad

- ✅ Contraste adecuado en ambos modos
- ✅ Icono visual + texto descriptivo
- ✅ Tamaño de fuente legible
- ✅ Colores que indican advertencia (amarillo/naranja)

## Notas Técnicas

- La advertencia usa `display: none` inicialmente
- Se muestra con `display: flex` para alinear contenido
- La animación se aplica automáticamente al cambiar display
- Los estilos están inline en el template para facilitar mantenimiento
- Compatible con todos los navegadores modernos
