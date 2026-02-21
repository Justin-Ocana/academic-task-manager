# Sistema de Documentos Adjuntos

## Descripción General
Sistema para subir, gestionar y descargar documentos adjuntos a tareas con control de permisos y aprobación.

## Características Principales

### 1. Configuración por Grupo
Cada grupo puede configurar:
- **Habilitar/Deshabilitar documentos**: Control total sobre si se permiten archivos adjuntos
- **Permisos de subida**:
  - `all`: Todos los miembros pueden subir documentos
  - `leader`: Solo el líder puede subir documentos
  - `approval`: Todos pueden subir, pero requiere aprobación del líder

### 2. Modelo TaskAttachment
```python
- task: Tarea a la que pertenece
- file: Archivo físico (almacenado en /media/task_files/group_X/task_Y/)
- original_filename: Nombre original del archivo
- file_size: Tamaño en bytes
- file_type: Tipo MIME del archivo
- status: pending/approved/rejected
- uploaded_by: Usuario que subió el archivo
- reviewed_by: Líder que aprobó/rechazó (si aplica)
```

### 3. Límites y Restricciones
- **Tamaño máximo**: 10 MB por archivo
- **Tipos permitidos**:
  - PDF (.pdf)
  - Word (.doc, .docx)
  - Excel (.xls, .xlsx)
  - PowerPoint (.ppt, .pptx)
  - Texto plano (.txt)
- **Tipos bloqueados**: .exe, .zip, .js, .bat, etc.

### 4. Estructura de Archivos
```
media/
└── task_files/
    └── group_12/
        └── task_55/
            ├── documento-1.pdf
            └── presentacion-final.pptx
```

## Flujo de Trabajo

### Caso 1: Subida Libre (all)
1. Usuario sube documento
2. Se valida tamaño y tipo
3. Se guarda con status='approved'
4. Aparece inmediatamente en la tarea

### Caso 2: Solo Líder (leader)
1. Solo el líder ve el botón de subir
2. Sube documento
3. Se guarda con status='approved'
4. Aparece inmediatamente

### Caso 3: Requiere Aprobación (approval)
1. Usuario sube documento
2. Se guarda con status='pending'
3. Líder recibe notificación (reutiliza sistema de solicitudes)
4. Líder aprueba/rechaza
5. Si aprueba: status='approved', visible para todos
6. Si rechaza: status='rejected', se elimina o marca como rechazado

## Seguridad

### Validaciones
- Verificar pertenencia al grupo antes de descargar
- Verificar permisos antes de subir
- Validar tipo de archivo en servidor (no solo cliente)
- Sanitizar nombres de archivo

### Descarga Segura
```python
@login_required
def download_attachment(request, attachment_id):
    attachment = get_object_or_404(TaskAttachment, id=attachment_id)
    
    # Verificar pertenencia al grupo
    if not attachment.task.group.members.filter(user=request.user).exists():
        return HttpResponseForbidden()
    
    # Verificar que esté aprobado
    if attachment.status != 'approved':
        return HttpResponseForbidden()
    
    return FileResponse(attachment.file.open(), as_attachment=True)
```

## Interfaz de Usuario

### Indicadores Visuales
- **En lista de tareas**: Icono de clip 📎 si tiene documentos
- **En detalle de tarea**: Sección "Documentos Adjuntos"
  - Lista de archivos con nombre, tamaño, fecha
  - Botón de descarga
  - Icono según tipo de archivo

### Estados de Documentos
- ✅ **Aprobado**: Verde, descargable
- ⏳ **Pendiente**: Amarillo, solo visible para uploader y líder
- ❌ **Rechazado**: Rojo, solo visible para uploader

## Integración con Sistema Existente

### Reutilización de Solicitudes
Las solicitudes de aprobación de documentos se manejan igual que las solicitudes de tareas:
- Aparecen en la página de solicitudes del grupo
- Mismo flujo de aprobación/rechazo
- Mismas notificaciones

### Permisos
Se integra con el sistema de permisos existente:
- Respeta roles (líder, co-líder, miembro)
- Respeta configuración del grupo
- Respeta estado de baneo/advertencias

## Próximas Mejoras (Futuro)
- [ ] Documentos en comentarios
- [ ] Previsualización de PDFs
- [ ] Versionado de documentos
- [ ] Migración a S3/Cloudinary para producción
- [ ] Compresión automática
- [ ] Escaneo de virus

## Notas Técnicas
- Los archivos NO se guardan en la base de datos
- Solo se guarda la ruta y metadata
- En producción, considerar migrar a S3
- Whitenoise NO sirve archivos media, solo static
- En desarrollo, Django sirve media automáticamente
