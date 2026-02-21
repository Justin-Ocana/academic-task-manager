import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def validate_name(value):
    """
    Valida que el nombre sea realista y permita hasta 2 nombres.
    
    Reglas:
    - Solo letras (a-z, A-Z, áéíóúñÑ) y un espacio
    - Longitud total: 3 a 30 caracteres
    - Cada nombre: 2 a 15 caracteres
    - Máximo 1 espacio (para separar dos nombres)
    - Máximo 2 letras repetidas seguidas
    - Sin números ni símbolos especiales
    - Sin espacios al inicio, final o múltiples seguidos
    """
    # Verificar longitud total
    if len(value) < 3:
        raise ValidationError(
            _('El nombre debe tener al menos 3 caracteres.'),
            code='too_short'
        )
    
    if len(value) > 30:
        raise ValidationError(
            _('El nombre no puede tener más de 30 caracteres.'),
            code='too_long'
        )
    
    # Solo letras, un espacio, acentos y ñ
    if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ]+(\s[a-zA-ZáéíóúÁÉÍÓÚñÑ]+)?$', value):
        raise ValidationError(
            _('El nombre solo puede contener letras y un espacio (para dos nombres).'),
            code='invalid_characters'
        )
    
    # Verificar espacios al inicio o final
    if value != value.strip():
        raise ValidationError(
            _('El nombre no puede tener espacios al inicio o final.'),
            code='invalid_spaces'
        )
    
    # Verificar múltiples espacios seguidos
    if '  ' in value:
        raise ValidationError(
            _('El nombre no puede tener espacios múltiples.'),
            code='multiple_spaces'
        )
    
    # Máximo 2 caracteres repetidos seguidos
    if re.search(r'(.)\1{2,}', value):
        raise ValidationError(
            _('El nombre no puede tener más de 2 letras iguales seguidas.'),
            code='too_many_repeated'
        )
    
    # Verificar que cada nombre tenga entre 2 y 15 caracteres
    nombres = value.split()
    for nombre in nombres:
        if len(nombre) < 2:
            raise ValidationError(
                _('Cada nombre debe tener al menos 2 caracteres.'),
                code='name_too_short'
            )
        if len(nombre) > 15:
            raise ValidationError(
                _('Cada nombre no puede tener más de 15 caracteres.'),
                code='name_too_long'
            )
    
    # Verificar máximo 2 nombres
    if len(nombres) > 2:
        raise ValidationError(
            _('Solo se permiten máximo 2 nombres (ej: Juan Pablo).'),
            code='too_many_names'
        )
    
    return value


def capitalize_name(value):
    """
    Capitaliza cada nombre correctamente.
    Ejemplo: juan pablo → Juan Pablo
    """
    if not value:
        return value
    
    # Capitalizar cada palabra
    return ' '.join(word.capitalize() for word in value.split())


def validate_subject_name(value):
    """
    Valida que el nombre de la materia sea realista.
    
    Reglas:
    - Longitud: 2 a 40 caracteres
    - Permite letras, números, espacios y algunos símbolos comunes
    - Máximo 3 caracteres repetidos seguidos
    """
    # Verificar longitud
    if len(value) < 2:
        raise ValidationError(
            _('El nombre de la materia debe tener al menos 2 caracteres.'),
            code='too_short'
        )
    
    if len(value) > 40:
        raise ValidationError(
            _('El nombre de la materia no puede tener más de 40 caracteres.'),
            code='too_long'
        )
    
    # Permitir letras, números, espacios, guiones y paréntesis
    if not re.match(r'^[a-zA-Z0-9áéíóúÁÉÍÓÚñÑ\s\-()]+$', value):
        raise ValidationError(
            _('El nombre de la materia contiene caracteres no permitidos.'),
            code='invalid_characters'
        )
    
    # Máximo 3 caracteres repetidos seguidos
    if re.search(r'(.)\1{3,}', value):
        raise ValidationError(
            _('El nombre no puede tener más de 3 caracteres iguales seguidos.'),
            code='too_many_repeated'
        )
    
    # No permitir solo espacios
    if value.strip() == '':
        raise ValidationError(
            _('El nombre de la materia no puede estar vacío.'),
            code='empty'
        )
    
    return value
