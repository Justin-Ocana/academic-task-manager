from django import forms
from .models import Group, JoinRequest


class CreateGroupForm(forms.ModelForm):
    """Formulario para crear un grupo"""
    
    class Meta:
        model = Group
        fields = [
            'name', 
            'description', 
            'max_members', 
            'entry_type',
            'task_create_permission',
            'task_edit_permission',
            'task_delete_permission',
            'task_revert_permission',
            'subject_permission',
            'documents_enabled',
            'document_upload_permission',
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Ej: Matemáticas 3ro A'}),
            'description': forms.Textarea(attrs={'class': 'form-textarea', 'placeholder': 'Descripción del grupo', 'rows': 3}),
            'max_members': forms.NumberInput(attrs={'class': 'form-input', 'min': 1, 'max': 100}),
            'entry_type': forms.Select(attrs={'class': 'form-select'}),
            'task_create_permission': forms.Select(attrs={'class': 'form-select'}),
            'task_edit_permission': forms.Select(attrs={'class': 'form-select'}),
            'task_delete_permission': forms.Select(attrs={'class': 'form-select'}),
            'task_revert_permission': forms.Select(attrs={'class': 'form-select'}),
            'subject_permission': forms.Select(attrs={'class': 'form-select'}),
            'documents_enabled': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
            'document_upload_permission': forms.Select(attrs={'class': 'form-select'}),
        }
        labels = {
            'name': 'Nombre del Grupo',
            'description': 'Descripción',
            'max_members': 'Máximo de Estudiantes',
            'entry_type': 'Tipo de Ingreso',
            'task_create_permission': 'Quién puede crear tareas',
            'task_edit_permission': 'Quién puede editar tareas',
            'task_delete_permission': 'Quién puede eliminar tareas',
            'task_revert_permission': 'Quién puede revertir cambios',
            'subject_permission': 'Permisos de materias',
            'documents_enabled': 'Habilitar documentos adjuntos',
            'document_upload_permission': 'Quién puede subir documentos',
        }


class JoinGroupForm(forms.Form):
    """Formulario para unirse a un grupo con código"""
    
    invite_code = forms.CharField(
        max_length=10,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Ingresa el código',
            'style': 'text-transform: uppercase;'
        }),
        label='Código de Invitación'
    )
    message = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-textarea',
            'placeholder': 'Mensaje opcional para el líder (si requiere aprobación)',
            'rows': 3
        }),
        label='Mensaje (Opcional)'
    )
    
    def clean_invite_code(self):
        code = self.cleaned_data['invite_code'].upper().strip()
        try:
            group = Group.objects.get(invite_code=code, is_invite_active=True)
        except Group.DoesNotExist:
            raise forms.ValidationError('Código inválido o inactivo')
        return code


class GroupSettingsForm(forms.ModelForm):
    """Formulario para editar configuración del grupo"""
    
    class Meta:
        model = Group
        fields = [
            'name',
            'description',
            'max_members',
            'entry_type',
            'is_invite_active',
            'task_create_permission',
            'task_edit_permission',
            'task_delete_permission',
            'task_revert_permission',
            'subject_permission',
            'content_moderation',
            'documents_enabled',
            'document_upload_permission',
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input'}),
            'description': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 3}),
            'max_members': forms.NumberInput(attrs={'class': 'form-input'}),
            'entry_type': forms.Select(attrs={'class': 'form-select'}),
            'is_invite_active': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
            'task_create_permission': forms.Select(attrs={'class': 'form-select'}),
            'task_edit_permission': forms.Select(attrs={'class': 'form-select'}),
            'task_delete_permission': forms.Select(attrs={'class': 'form-select'}),
            'task_revert_permission': forms.Select(attrs={'class': 'form-select'}),
            'subject_permission': forms.Select(attrs={'class': 'form-select'}),
            'content_moderation': forms.Select(attrs={'class': 'form-select'}),
            'documents_enabled': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
            'document_upload_permission': forms.Select(attrs={'class': 'form-select'}),
        }
