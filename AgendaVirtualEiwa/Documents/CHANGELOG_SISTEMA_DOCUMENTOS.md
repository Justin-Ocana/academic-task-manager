# Changelog - Sistema de Documentos Adjuntos

## Fecha: 2026-02-06

### ✅ Implementado

#### Modelos
- ✅ `TaskAttachment` - Modelo para archivos adjuntos
- ✅ Campos en `Group` para habilitar documentos y permisos
- ✅ Estructura de archivos: `/media/task_files/group_X/task_Y/`

#### Configuración
- ✅ MEDIA_ROOT y MEDIA_URL configurados
- ✅ Límite de 10 MB por archivo
- ✅ Tipos permitidos: PDF, Word, Excel, PowerPoint, TXT
- ✅ Tipos bloqueados: .exe, .bat, .zip, etc.

#### Formularios
- ✅ Campo de documentos en creación de grupos
- ✅ Campo de documentos en configuración de grupos
- ✅ Campo de documentos en creación de tareas
- ✅ Checkboxes mejorados con estilos personalizados
- ✅ Modo oscuro para todos los formularios

#### Vistas
- ✅ Subir documentos al crear tarea
- ✅ Descargar documentos con verificación de permisos
- ✅ Mostrar documentos en detalle de tarea
- ✅ Filtrado de documentos según permisos

#### Templates
- ✅ Sección de documentos en task_detail (solo lectura)
- ✅ Campo de subida en task_form
- ✅ Visualización de archivos seleccionados con JavaScript
- ✅ Drag & drop para subir archivos
- ✅ Estilos optimizados para modo oscuro

#### Permisos
- ✅ `all` - Todos pueden subir
- ✅ `leader` - Solo líder puede subir
- ✅ `approval` - Todos pueden subir pero requiere aprobación

### 📝 Notas
- Los documentos se suben al crear/editar tareas
- Solo se muestran documentos aprobados en task_detail
- Los archivos se almacenan en el servidor (no en BD)
- Sistema preparado para migrar a S3 en el futuro

### 🎨 Mejoras Visuales
- Checkboxes personalizados con gradiente azul
- Animación de check
- Hover effects
- Modo oscuro completo
- Iconos según tipo de archivo

### 🔒 Seguridad
- Validación de tamaño en cliente y servidor
- Validación de tipo MIME
- Validación de extensión
- Bloqueo de archivos peligrosos
- Verificación de permisos antes de descargar
- Nombres de archivo sanitizados

### 🚀 Próximos Pasos (Opcional)
- [ ] Editar documentos en formulario de edición de tareas
- [ ] Eliminar documentos individuales
- [ ] Previsualización de PDFs
- [ ] Compresión automática
- [ ] Migración a S3 para producción
