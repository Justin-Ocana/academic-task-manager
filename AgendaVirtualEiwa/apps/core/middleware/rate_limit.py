# Middleware para rate limiting
from django.core.cache import cache
from django.http import JsonResponse
from django.conf import settings
import time


class RateLimitMiddleware:
    """
    Middleware para limitar la cantidad de peticiones por usuario/IP
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        
        # Configuración de límites
        self.limits = {
            'default': (100, 60),  # 100 peticiones por minuto
            'login': (5, 300),     # 5 intentos de login por 5 minutos
            'create_group': (10, 3600),  # 10 grupos por hora
            'create_task': (50, 3600),   # 50 tareas por hora
            'join_group': (20, 3600),    # 20 uniones por hora
        }
    
    def __call__(self, request):
        # Obtener identificador (usuario o IP)
        identifier = self.get_identifier(request)
        
        # Determinar tipo de petición
        rate_type = self.get_rate_type(request)
        
        # Verificar límite
        if not self.check_rate_limit(identifier, rate_type):
            return JsonResponse({
                'error': 'Demasiadas peticiones. Por favor espera un momento.',
                'retry_after': self.get_retry_after(identifier, rate_type)
            }, status=429)
        
        response = self.get_response(request)
        return response
    
    def get_identifier(self, request):
        """Obtiene identificador único del usuario o IP"""
        if request.user.is_authenticated:
            return f"user_{request.user.id}"
        return f"ip_{self.get_client_ip(request)}"
    
    def get_client_ip(self, request):
        """Obtiene IP del cliente"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def get_rate_type(self, request):
        """Determina el tipo de rate limit según la URL"""
        path = request.path
        
        if 'login' in path or 'signin' in path:
            return 'login'
        elif 'groups/create' in path:
            return 'create_group'
        elif 'tasks/create' in path:
            return 'create_task'
        elif 'groups/join' in path:
            return 'join_group'
        
        return 'default'
    
    def check_rate_limit(self, identifier, rate_type):
        """Verifica si el usuario ha excedido el límite"""
        max_requests, window = self.limits.get(rate_type, self.limits['default'])
        
        cache_key = f"rate_limit_{rate_type}_{identifier}"
        
        # Obtener peticiones actuales
        requests = cache.get(cache_key, [])
        now = time.time()
        
        # Filtrar peticiones dentro de la ventana de tiempo
        requests = [req_time for req_time in requests if now - req_time < window]
        
        # Verificar límite
        if len(requests) >= max_requests:
            return False
        
        # Agregar petición actual
        requests.append(now)
        cache.set(cache_key, requests, window)
        
        return True
    
    def get_retry_after(self, identifier, rate_type):
        """Obtiene tiempo de espera en segundos"""
        _, window = self.limits.get(rate_type, self.limits['default'])
        cache_key = f"rate_limit_{rate_type}_{identifier}"
        requests = cache.get(cache_key, [])
        
        if requests:
            oldest_request = min(requests)
            return int(window - (time.time() - oldest_request))
        
        return 0


# Decorador para rate limiting en vistas específicas
def rate_limit(max_requests=10, window=60):
    """
    Decorador para limitar peticiones en vistas específicas
    
    Uso:
    @rate_limit(max_requests=5, window=300)
    def my_view(request):
        ...
    """
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            identifier = f"user_{request.user.id}" if request.user.is_authenticated else f"ip_{request.META.get('REMOTE_ADDR')}"
            cache_key = f"rate_limit_{view_func.__name__}_{identifier}"
            
            requests = cache.get(cache_key, [])
            now = time.time()
            
            # Filtrar peticiones dentro de la ventana
            requests = [req_time for req_time in requests if now - req_time < window]
            
            if len(requests) >= max_requests:
                return JsonResponse({
                    'error': 'Demasiadas peticiones. Por favor espera un momento.'
                }, status=429)
            
            requests.append(now)
            cache.set(cache_key, requests, window)
            
            return view_func(request, *args, **kwargs)
        
        return wrapper
    return decorator
