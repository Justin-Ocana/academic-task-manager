from django import forms
from django.conf import settings
from .models import Task, TaskAttachment
import os


class TaskAttachmentForm(forms.ModelForm):
    """Formulario para subir documentos adjuntos"""
    
    class Meta:
        model = TaskAttachment
        fields = ['file']
        widgets = {
            'file': forms.FileInput(attrs={
                'class': 'form-file-input',
                'accept': '.pdf,.doc,.docx,.xls,.xlsx,.ppt,.pptx,.txt'
            })
        }
    
    def clean_file(self):
        file = self.cleaned_data.get('file')
        
        if not file:
            raise forms.ValidationError('Debes seleccionar un archivo')
        
        # Validar tamaño
        if file.size > settings.MAX_UPLOAD_SIZE:
            max_size_mb = settings.MAX_UPLOAD_SIZE / (1024 * 1024)
            raise forms.ValidationError(f'El archivo es demasiado grande. Máximo: {max_size_mb} MB')
        
        # Validar tipo de archivo
        file_type = file.content_type
        if file_type not in settings.ALLOWED_DOCUMENT_TYPES:
            raise forms.ValidationError('Tipo de archivo no permitido. Solo se permiten: PDF, Word, Excel, PowerPoint y TXT')
        
        # Validar extensión (seguridad adicional)
        ext = os.path.splitext(file.name)[1].lower()
        allowed_extensions = ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.txt']
        if ext not in allowed_extensions:
            raise forms.ValidationError('Extensión de archivo no permitida')
        
        # Bloquear extensiones peligrosas
        dangerous_extensions = ['.exe', '.bat', '.cmd', '.sh', '.js', '.jar', '.zip', '.rar']
        if ext in dangerous_extensions:
            raise forms.ValidationError('Este tipo de archivo está bloqueado por seguridad')
        
        return file



class TaskForm(forms.ModelForm):
    """Formulario para crear/editar tareas"""
    
    class Meta:
        model = Task
        fields = ['subject', 'title', 'description', 'pages', 'assigned_date', 'due_date', 'priority']
        widgets = {
            'subject': forms.Select(attrs={'class': 'form-select'}),
            'title': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Título de la tarea'}),
            'description': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 4, 'placeholder': 'Descripción detallada'}),
            'pages': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Ej: 45-50'}),
            'assigned_date': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'due_date': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'priority': forms.Select(attrs={'class': 'form-select'}),
        }
    
    def __init__(self, *args, **kwargs):
        group = kwargs.pop('group', None)
        super().__init__(*args, **kwargs)
        
        # Filtrar materias por grupo
        if group:
            from apps.subjects.models import Subject
            self.fields['subject'].queryset = Subject.objects.filter(group=group)
