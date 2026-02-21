from django import forms
from .models import Subject, SubjectRequest


class SubjectForm(forms.ModelForm):
    """Formulario para crear/editar materias"""
    
    class Meta:
        model = Subject
        fields = ['name', 'color']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Ej: Matemáticas'
            }),
            'color': forms.Select(attrs={
                'class': 'form-select color-select'
            })
        }
        labels = {
            'name': 'Nombre de la Materia',
            'color': 'Color'
        }


class SubjectRequestForm(forms.ModelForm):
    """Formulario para solicitar agregar una materia"""
    
    class Meta:
        model = SubjectRequest
        fields = ['name', 'color']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Ej: Matemáticas'
            }),
            'color': forms.Select(attrs={
                'class': 'form-select color-select'
            })
        }
        labels = {
            'name': 'Nombre de la Materia',
            'color': 'Color'
        }
