from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User
from .validators import validate_name, capitalize_name


class RegisterForm(UserCreationForm):
    nombre = forms.CharField(
        max_length=30,
        min_length=3,
        required=True,
        validators=[validate_name],
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Ej: Juan Pablo',
            'maxlength': '30',
            'pattern': '[a-zA-ZáéíóúÁÉÍÓÚñÑ]+(\\s[a-zA-ZáéíóúÁÉÍÓÚñÑ]+)?',
            'title': '1-2 nombres, solo letras, 3-30 caracteres'
        }),
        help_text='Permite 1-2 nombres (ej: Juan Pablo). Solo letras, 3-30 caracteres.'
    )
    apellido = forms.CharField(
        max_length=30,
        min_length=3,
        required=True,
        validators=[validate_name],
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Ej: García López',
            'maxlength': '30',
            'pattern': '[a-zA-ZáéíóúÁÉÍÓÚñÑ]+(\\s[a-zA-ZáéíóúÁÉÍÓÚñÑ]+)?',
            'title': '1-2 apellidos, solo letras, 3-30 caracteres'
        }),
        help_text='Permite 1-2 apellidos (ej: García López). Solo letras, 3-30 caracteres.'
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-input',
            'placeholder': 'tu@email.com'
        })
    )
    password1 = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Mínimo 8 caracteres'
        })
    )
    password2 = forms.CharField(
        label='Confirmar Contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Repite tu contraseña'
        })
    )

    class Meta:
        model = User
        fields = ['nombre', 'apellido', 'email', 'password1', 'password2']
    
    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre', '').strip()
        if nombre:
            # Capitalizar automáticamente
            nombre = capitalize_name(nombre)
        return nombre
    
    def clean_apellido(self):
        apellido = self.cleaned_data.get('apellido', '').strip()
        if apellido:
            # Capitalizar automáticamente
            apellido = capitalize_name(apellido)
        return apellido

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['email']
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


class LoginForm(AuthenticationForm):
    username = forms.EmailField(
        label='Correo Electrónico',
        widget=forms.EmailInput(attrs={
            'class': 'form-input',
            'placeholder': 'tu@email.com'
        })
    )
    password = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Tu contraseña'
        })
    )
