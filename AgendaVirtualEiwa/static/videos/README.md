# 📹 Videos para la Página de Inicio

Esta carpeta contiene los videos demostrativos de la Agenda Virtual Eiwa.

## 📁 Estructura de Archivos

Coloca tus videos con los siguientes nombres:

### Video Principal (Hero)
- **demo-principal.mp4** - Video demo completo (60-90 segundos)
  - Resolución recomendada: 1920x1080 (Full HD)
  - Formato: MP4 (H.264)
  - Duración: 60-90 segundos
  - Contenido: Tour general de la plataforma

### Videos de Características
- **feature-tasks.mp4** - Demo de gestión de tareas (15-20 segundos)
  - Muestra: Crear, editar, completar tareas
  
- **feature-calendar.mp4** - Demo del calendario (15-20 segundos)
  - Muestra: Vista de calendario, filtros, navegación
  
- **feature-groups.mp4** - Demo de grupos colaborativos (15-20 segundos)
  - Muestra: Crear grupo, unirse, permisos

## 🖼️ Thumbnails (Imágenes de Vista Previa)

Coloca las imágenes en `static/img/`:

- **video-thumbnail.jpg** - Thumbnail del video principal
- **feature-tasks.jpg** - Thumbnail de tareas
- **feature-calendar.jpg** - Thumbnail de calendario
- **feature-groups.jpg** - Thumbnail de grupos

Resolución recomendada: 1280x720 (16:9)

## ⚙️ Especificaciones Técnicas

### Formato de Video
- **Códec**: H.264
- **Contenedor**: MP4
- **Bitrate**: 2-5 Mbps
- **FPS**: 30 fps
- **Audio**: AAC, 128 kbps (opcional)

### Optimización
Para web, usa estas configuraciones en tu editor de video:
- Compresión: Alta calidad, tamaño optimizado
- Perfil: Baseline o Main
- Nivel: 4.0 o superior

### Herramientas Recomendadas
- **OBS Studio** - Para grabar pantalla
- **DaVinci Resolve** - Para editar (gratis)
- **HandBrake** - Para comprimir videos
- **FFmpeg** - Para conversión por línea de comandos

## 📝 Ejemplo de Comando FFmpeg

Para optimizar un video para web:

```bash
ffmpeg -i input.mp4 -c:v libx264 -preset slow -crf 22 -c:a aac -b:a 128k -movflags +faststart output.mp4
```

## 🎬 Consejos para Grabar

1. **Resolución**: Graba en 1920x1080 o superior
2. **Limpieza**: Cierra notificaciones y aplicaciones innecesarias
3. **Cursor**: Usa un cursor destacado o resaltador
4. **Velocidad**: Mueve el mouse suavemente
5. **Audio**: Si incluyes narración, usa un buen micrófono
6. **Duración**: Mantén los videos cortos y al punto
7. **Transiciones**: Usa cortes limpios entre escenas

## 🎨 Estilo Visual

- Usa el tema claro de la aplicación
- Muestra datos realistas (usa el script populate_test_data.py)
- Incluye interacciones naturales
- Destaca las características principales

## 📱 Consideraciones Móviles

Los videos se adaptan automáticamente:
- En desktop: Tamaño completo con controles
- En móvil: Tamaño reducido con opción de pantalla completa
- Los videos de características se reproducen en loop al hacer click

## 🔄 Actualización de Videos

Para actualizar un video:
1. Reemplaza el archivo en esta carpeta
2. Limpia la caché del navegador (Ctrl+Shift+R)
3. Verifica que el nuevo video se cargue correctamente

## ⚠️ Notas Importantes

- Los videos NO se incluyen en el repositorio Git (están en .gitignore)
- Mantén los archivos de video lo más pequeños posible
- Considera usar un CDN para videos en producción
- Los thumbnails son obligatorios para mejor experiencia de usuario

## 📊 Tamaños Recomendados

- Video principal: < 50 MB
- Videos de características: < 10 MB cada uno
- Thumbnails: < 500 KB cada uno

## 🚀 Producción

Para producción, considera:
- Subir videos a YouTube/Vimeo y usar embed
- Usar un CDN como Cloudflare o AWS CloudFront
- Implementar lazy loading (ya incluido en el código)
- Ofrecer múltiples resoluciones según el dispositivo
