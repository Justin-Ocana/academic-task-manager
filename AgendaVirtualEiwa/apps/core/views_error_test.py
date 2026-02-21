"""
Vistas de prueba para páginas de error personalizadas
Solo para desarrollo - NO usar en producción
"""

from django.shortcuts import render
from django.views.decorators.http import require_http_methods


@require_http_methods(["GET"])
def test_404(request):
    """Vista de prueba para página 404"""
    return render(request, '404.html', status=404)


@require_http_methods(["GET"])
def test_403(request):
    """Vista de prueba para página 403"""
    return render(request, '403.html', status=403)


@require_http_methods(["GET"])
def test_500(request):
    """Vista de prueba para página 500"""
    return render(request, '500.html', status=500)
