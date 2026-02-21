# Middleware de seguridad adicional
from django.http import HttpResponseForbidden
from django.core.exceptions import PermissionDenied
import re


class SecurityMiddleware:
    """
    Middleware para agregar capas adicionales de seguridad
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        
        # Patrones sospechosos
        self.suspicious_patterns = [
            r'<script',
            r'javascript:',
            r'onerror=',
            r'onclick=',
            r'\.\./\.\.',  # Path traversal
            r'union.*select',  # SQL injection
            r'drop.*table',
        ]
    
    def __call__(self, request):
        # Verificar patrones sospechosos en parámetros
        if self.contains_suspicious_content(request):
            return HttpResponseForbidden('Petición sospechosa detectada')
        
        # Verificar CSRF en peticiones POST
        if request.method == 'POST' and not self.is_ajax(request):
            if not request.META.get('CSRF_COOKIE'):
                return HttpResponseForbidden('Token CSRF faltante')
        
        response = self.get_response(request)
        
        # Agregar headers de seguridad
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        return response
    
    def contains_suspicious_content(self, request):
        """Verifica si la petición contiene contenido sospechoso"""
        # Verificar GET params
        for key, value in request.GET.items():
            if self.is_suspicious(value):
                return True
        
        # Verificar POST params
        for key, value in request.POST.items():
            if self.is_suspicious(str(value)):
                return True
        
        return False
    
    def is_suspicious(self, text):
        """Verifica si un texto contiene patrones sospechosos"""
        text_lower = text.lower()
        for pattern in self.suspicious_patterns:
            if re.search(pattern, text_lower, re.IGNORECASE):
                return True
        return False
    
    def is_ajax(self, request):
        """Verifica si es una petición AJAX"""
        return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'


class PermissionMiddleware:
    """
    Middleware para verificar permisos en todas las vistas
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        
        # URLs que requieren autenticación
        self.protected_urls = [
            r'^/dashboard/',
            r'^/groups/',
            r'^/tasks/',
            r'^/calendar/',
            r'^/notifications/',
            r'^/settings/',
        ]
        
        # URLs públicas
        self.public_urls = [
            r'^/$',
            r'^/login/',
            r'^/register/',
            r'^/terms/',
            r'^/static/',
            r'^/media/',
        ]
    
    def __call__(self, request):
        path = request.path
        
        # Verificar si la URL requiere autenticación
        if self.requires_authentication(path):
            if not request.user.is_authenticated:
                from django.shortcuts import redirect
                return redirect('login')
        
        response = self.get_response(request)
        return response
    
    def requires_authentication(self, path):
        """Verifica si una URL requiere autenticación"""
        # Verificar URLs públicas
        for pattern in self.public_urls:
            if re.match(pattern, path):
                return False
        
        # Verificar URLs protegidas
        for pattern in self.protected_urls:
            if re.match(pattern, path):
                return True
        
        return False
