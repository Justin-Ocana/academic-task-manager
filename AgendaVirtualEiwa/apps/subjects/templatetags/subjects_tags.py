from django import template
from apps.subjects.models import Subject

register = template.Library()


@register.filter
def get_subject_name(subject_id):
    """Obtener el nombre de una materia por su ID"""
    try:
        subject = Subject.objects.get(id=subject_id)
        return subject.name
    except Subject.DoesNotExist:
        return "Materia no encontrada"
