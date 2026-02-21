# PWA - Agenda Virtual EIWA

## ✅ Configuración Completada

Tu aplicación ahora está configurada como **Progressive Web App (PWA)** y puede instalarse en dispositivos móviles.

## 📱 Cómo Agregar a Pantalla de Inicio

### En Android (Chrome/Edge)
1. Abre la app en el navegador
2. Toca el menú (⋮) en la esquina superior derecha
3. Selecciona **"Agregar a pantalla de inicio"** o **"Instalar app"**
4. Confirma la instalación
5. ¡El icono EIWALOGOMOBILE.png aparecerá en tu pantalla de inicio!

### En iOS (Safari)
1. Abre la app en Safari
2. Toca el botón de compartir (□↑) en la parte inferior
3. Desplázate y selecciona **"Agregar a pantalla de inicio"**
4. Edita el nombre si deseas
5. Toca **"Agregar"**
6. ¡El icono aparecerá en tu pantalla de inicio!

## 🎨 Configuración Implementada

### Archivos Creados:
- ✅ `static/manifest.json` - Configuración de la PWA
- ✅ `static/service-worker.js` - Service Worker para funcionalidad offline

### Archivos Modificados:
- ✅ `apps/core/templates/Dashboard/base_dashboard.html`
- ✅ `apps/core/templates/Index/base.html`

### Características:
- **Nombre**: Agenda Virtual EIWA
- **Nombre corto**: EIWA
- **Color de tema**: #213E89 (Azul EIWA)
- **Icono principal**: EIWALOGOMOBILE.png
- **Modo de visualización**: Standalone (pantalla completa sin barra del navegador)
- **Orientación**: Portrait (vertical)
- **Idioma**: Español (México)

## 🔧 Características PWA

### ✅ Instalable
- Los usuarios pueden instalar la app en su dispositivo
- Aparece como una app nativa en la pantalla de inicio
- Se abre en pantalla completa sin la barra del navegador

### ✅ Service Worker
- Cache básico de recursos estáticos
- Mejora la velocidad de carga
- Base para funcionalidad offline futura

### ✅ Manifest
- Define cómo se ve y comporta la app cuando está instalada
- Configura iconos, colores y orientación
- Optimizado para dispositivos móviles

## 🚀 Próximas Mejoras Posibles

1. **Modo Offline Completo**
   - Guardar datos en IndexedDB
   - Sincronización cuando vuelva la conexión

2. **Notificaciones Push Nativas**
   - Notificaciones incluso cuando la app está cerrada
   - Integración con Firebase Cloud Messaging

3. **Actualización Automática**
   - Detectar nuevas versiones
   - Actualizar el Service Worker automáticamente

4. **Más Iconos**
   - Crear iconos de diferentes tamaños (72x72, 96x96, 128x128, 144x144, 152x152, 192x192, 384x384, 512x512)
   - Iconos adaptables para diferentes dispositivos

## 📝 Notas Importantes

- **HTTPS Requerido**: Las PWA solo funcionan en HTTPS (tu app en Render ya lo tiene)
- **Iconos**: Actualmente usa EIWALOGOMOBILE.png - considera crear versiones optimizadas de diferentes tamaños
- **Cache**: El Service Worker cachea recursos básicos - puedes expandir esto según necesites
- **Compatibilidad**: Funciona en Chrome, Edge, Safari (iOS 11.3+), Firefox, Opera

## 🧪 Cómo Probar

1. Despliega los cambios en Render
2. Abre la app en tu móvil
3. Busca la opción "Agregar a pantalla de inicio"
4. Instala y verifica que el icono sea correcto
5. Abre la app instalada y verifica que funcione en modo standalone

## 🎯 Verificación

Para verificar que todo está configurado correctamente:

1. Abre Chrome DevTools (F12)
2. Ve a la pestaña **"Application"**
3. En el menú lateral:
   - **Manifest**: Verifica que se cargue correctamente
   - **Service Workers**: Verifica que esté registrado y activo
   - **Cache Storage**: Verifica que los recursos se estén cacheando

## 🐛 Troubleshooting

**El icono no aparece correctamente:**
- Verifica que EIWALOGOMOBILE.png exista en `/static/img/`
- Asegúrate de que el archivo sea PNG
- Tamaño recomendado: mínimo 192x192px

**No aparece la opción de instalar:**
- Verifica que estés en HTTPS
- Asegúrate de que el manifest.json se cargue correctamente
- Revisa la consola del navegador por errores

**Service Worker no se registra:**
- Verifica que service-worker.js esté en `/static/`
- Revisa la consola por errores de registro
- Asegúrate de que la ruta sea correcta

---

**Fecha de implementación**: Diciembre 2024
**Versión**: 1.0
